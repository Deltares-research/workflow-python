"""Jinja Makefile templating."""

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from workflowpy.methods.script import ScriptMethod
from workflowpy.utils.parsers import get_wildcards

if TYPE_CHECKING:
    from workflowpy.method import Method
    from workflowpy.rule import Rule


class JinjaMakeRule:
    """ViewModel for a Rule to print in a Jinja Makefile template."""

    def __init__(self, rule: "Rule"):
        self.rule = rule

    ## Private methods
    def _parse_variable(self, val: Any) -> str:
        """Parse $-references to Make variable format."""
        # Config variables
        if isinstance(val, str) and val.startswith("$config."):
            key = val.split(".")[1:]
            val = "$(" + "_".join(key).upper() + ")"
        # Rules
        elif isinstance(val, str) and val.startswith("$rules."):
            ref = self.rule.workflow.get_ref(val)
            val = ref.get_str_value(quote_str=False)
        # Wildcards
        elif isinstance(val, str) and val.startswith("$wildcards."):
            wc = val.split(".")[1]
            if self.is_pattern_rule and wc == self.rule.wildcards["repeat"][0]:
                val = "{" + wc + "}"
            else:
                val = "$(" + wc.upper() + ")"
        # Return the value converted to string
        return str(val)

    def _reduce_fields(self) -> List[str]:
        """Get field names that participate in reduce wildcards."""
        fields = []
        for wc in self.rule.wildcards["reduce"]:
            fields.extend(self.rule.wildcard_fields.get(wc, []))
        return list(set(fields))

    def _sub_repeat(self, val: str, char: str = "$*") -> str:
        """Substitute repeat wildcards for Make recipe context."""
        if self.is_pattern_rule:
            wc = self.rule.wildcards["repeat"][0]
            val = val.replace("{" + wc + "}", char)
        elif self.has_multiple_repeat_wildcards:
            for wc in self.rule.wildcards["repeat"]:
                val = val.replace("{" + wc + "}", "$(" + wc + ")")
        return val

    def _wrap_foreach(self, inner: str, wildcards: List[str]) -> str:
        """Wrap an expression in nested $(foreach) for the given wildcards."""
        expr = inner
        for wc in reversed(wildcards):
            expr = f"$(foreach {wc},$({wc.upper()}),{expr})"
        return expr

    ## Properties
    @property
    def foreach_wildcards(self) -> List[Dict[str, str]]:
        """Repeat wildcard names and Make variable names for foreach loops."""
        return [{"name": wc, "var": wc.upper()} for wc in self.rule.wildcards["repeat"]]

    @property
    def has_expand_wildcards(self) -> bool:
        """Return whether the Rule has any expand wildcards."""
        return len(self.rule.wildcards["expand"]) > 0

    @property
    def has_multiple_repeat_wildcards(self) -> bool:
        """Return whether the Rule has repeat wildcards."""
        return len(self.rule.wildcards["repeat"]) > 1

    @property
    def has_reduce_wildcards(self) -> bool:
        """Return whether the Rule has any reduce wildcards."""
        return len(self.rule.wildcards["reduce"]) > 0

    @property
    def is_pattern_rule(self) -> bool:
        """Check for one repeat wildcard (maps to Make %)."""
        return len(self.rule.wildcards["repeat"]) == 1

    @property
    def make_prereqs(self) -> List[str]:
        """Input paths formatted as Make prerequisites (non-reduce only)."""
        reduce_fields = self._reduce_fields()
        # Get the method inputs
        all_inputs = self.method.input.to_dict(
            mode="json",
            filter_types=Path,
            return_refs=True,
            posix_path=True,
        )
        # Get the prerequisites, excluding any that are part of reduce wildcards
        prereqs = []
        for key, val in all_inputs.items():
            if key in reduce_fields:
                continue
            prereqs.append(
                self._sub_repeat(self._parse_variable(val), char="%"),
            )
        return prereqs

    @property
    def make_targets(self) -> List[str]:
        """Output paths formatted as Make targets (non-expand case)."""
        output_templates = self.method.output.to_dict(
            mode="json", filter_types=Path, posix_path=True
        )
        return [self._sub_repeat(v, char="%") for v in output_templates.values()]

    @property
    def method(self) -> "Method":
        """Return the Method associated with this Rule."""
        return self.rule.method

    @property
    def method_name(self) -> str:
        """Return the name of the Method associated with this Rule."""
        return self.method.name

    @property
    def output_var_name(self) -> str:
        """Make variable name for the output target list."""
        return f"{self.rule_id.upper()}_OUTPUTS"

    @property
    def rule_id(self) -> str:
        """Return the rule_id of the Rule."""
        return self.rule.rule_id

    @property
    def output_foreach_expr(self) -> str:
        """Expand wildcard output targets."""
        expand_wcs = self.rule.wildcards["expand"]
        outputs = self.method.output.to_dict(
            mode="json", filter_types=Path, posix_path=True
        )
        # Separate outputs into dynamic (with expand wildcards)
        # and static (without expand wildcards)
        dynamic = []
        static = []
        for val in outputs.values():
            if any(get_wildcards(val, expand_wcs)):
                dynamic.append(val)
            else:
                static.append(val)

        # Create the input expression based on outputs where static is as is
        # and dynamic is wrapped in foreach for each expand wildcard
        parts = []
        if dynamic:
            patterns = []
            for val in dynamic:
                formatted = self._sub_repeat(val, char="%")
                for wc in expand_wcs:
                    formatted = formatted.replace("{" + wc + "}", "$(" + wc + ")")
                patterns.append(formatted)
            inner = " ".join(patterns)
            parts.append(self._wrap_foreach(inner, expand_wcs))

        for val in static:
            parts.append(self._sub_repeat(val, char="%"))

        # Return the combined expression
        return " ".join(parts)

    @property
    def prereqs_foreach_expr(self) -> Optional[str]:
        """Reduce wildcard input prerequisites."""
        reduce_wcs = self.rule.wildcards["reduce"]
        if not reduce_wcs:
            return None

        # Get the fields in reduce wildcards
        reduce_fields = self._reduce_fields()
        reduce_inputs = self.method.input.to_dict(
            mode="json",
            filter_types=Path,
            posix_path=True,
        )
        # Create a list of patterns for each reduce field,
        # substituting wildcards with Make variable format
        patterns = []
        for field in reduce_fields:
            if field not in reduce_inputs:
                continue
            val = reduce_inputs[field]
            formatted = self._sub_repeat(val, char="%")
            for wc in reduce_wcs:
                formatted = formatted.replace("{" + wc + "}", "$(" + wc + ")")
            patterns.append(formatted)

        if not patterns:
            return None
        inner = " ".join(patterns)
        # Return the formatted expression wrapped in foreach for each reduce wildcard
        return self._wrap_foreach(inner, reduce_wcs)

    @property
    def rule_all_input(self) -> Optional[List[str]]:
        """Return output paths for result rules (for the `all` target)."""
        if self.rule_id not in self.rule.workflow.rules.result_rules:
            return None
        paths = []
        for key in self.rule.output:
            for p in self.rule.output[key]:
                posix = p.as_posix()
                if posix not in paths:
                    paths.append(posix)
        return paths

    @property
    def script(self) -> Optional[str]:
        """Get the script path for ScriptMethod."""
        if isinstance(self.method, ScriptMethod):
            return self.method.input.script.as_posix()
        return None

    @property
    def workflowpy_shell_kwargs(self) -> Dict[str, str]:
        """Get the mapping of shell kwargs to Method component fields."""
        return self.method._kwargs_to_key_mapping()

    ## Public methods
    def shell_kwargs_formatted(self) -> Dict[str, str]:
        """Get shell kwargs with Make variable substitutions for the recipe."""
        reduce_fields = self._reduce_fields()
        reduce_wcs = self.rule.wildcards["reduce"]
        mapping = self.workflowpy_shell_kwargs
        result = {}
        for key, component_key in mapping.items():
            component, field = component_key.split(".")
            obj = getattr(self.method, component)
            raw_val = obj.to_dict(mode="json", posix_path=True, return_refs=True).get(
                field, ""
            )
            raw_str = self._parse_variable(str(raw_val))

            # Format the reduce wildcards
            if field in reduce_fields and reduce_wcs:
                # Get the value
                actual_val = obj.to_dict(mode="json", posix_path=True).get(field, "")
                formatted = self._sub_repeat(str(actual_val))
                for wc in reduce_wcs:
                    formatted = formatted.replace("{" + wc + "}", "$(" + wc + ")")
                result[key] = self._wrap_foreach(formatted, reduce_wcs)
            else:
                result[key] = self._sub_repeat(raw_str)
        return result
