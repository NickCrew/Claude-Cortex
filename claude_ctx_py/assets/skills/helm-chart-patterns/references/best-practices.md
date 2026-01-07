# Reference: Best Practices Summary

## Template Best Practices

1. **Use helper templates** for repeated logic
2. **Quote all strings**: `{{ .Values.name | quote }}`
3. **Validate with schema**: Always include values.schema.json
4. **Document all values**: Add comments in values.yaml
5. **Use consistent indentation**: `nindent` for proper YAML formatting
6. **Check for nil**: `{{- if .Values.optional }}` before accessing nested values
7. **Use `required`**: `{{ required "message" .Values.critical }}`

## Versioning and Compatibility

1. **Follow SemVer** for chart versions
2. **Pin dependencies** to specific versions or ranges
3. **Test upgrades** from previous versions
4. **Document breaking changes** in README
5. **Use appVersion** to track application version separately
6. **Set kubeVersion** to declare K8s compatibility

## Security Considerations

1. **Never commit secrets** to values files
2. **Use external secret management**: Sealed Secrets, External Secrets Operator
3. **Set security contexts** in all pods
4. **Drop capabilities**: `capabilities.drop: [ALL]`
5. **Use non-root users**: `runAsNonRoot: true`
6. **Enable seccomp**: `seccompProfile.type: RuntimeDefault`
7. **Sign packages** for production distribution

## Testing Strategy

1. **Lint before packaging**: `helm lint`
2. **Validate templates**: `helm template --debug`
3. **Test installations**: `helm test`
4. **Dry-run upgrades**: `helm upgrade --dry-run`
5. **Use CI/CD pipelines** for automated testing
6. **Test with multiple value combinations**
