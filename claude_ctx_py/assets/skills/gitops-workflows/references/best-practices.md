# Best Practices

## Repository Management

1. **Separate application and infrastructure repos** for different ownership and access control
2. **Use semantic versioning** for releases and tags
3. **Implement branch protection** on main branches
4. **Require pull request reviews** for production changes
5. **Tag production releases** for easy rollback reference
6. **Document promotion workflows** in repository README

## Security

1. **Never commit unencrypted secrets** to Git repositories
2. **Use External Secrets Operator** for cloud-native secret management
3. **Implement least-privilege RBAC** for GitOps tools
4. **Enable audit logging** for all sync operations
5. **Use separate service accounts** per application
6. **Scan manifests** for security issues in CI pipeline

## Sync Policies

1. **Use automated sync** for non-production environments
2. **Require manual approval** for production deployments
3. **Configure sync windows** for maintenance periods
4. **Implement health checks** for custom resources
5. **Use selective sync** for large applications
6. **Test sync policies** in staging before production

## Operations

1. **Monitor sync status** with alerting for failures
2. **Implement progressive delivery** for high-risk changes
3. **Test rollback procedures** regularly
4. **Document disaster recovery** processes
5. **Use resource hooks** for migration tasks
6. **Implement backup strategies** for Git repositories

## Multi-Environment

1. **Use consistent naming** across environments
2. **Minimize environment differences** (only necessary variations)
3. **Test promotion workflows** end-to-end
4. **Automate promotion** where possible
5. **Maintain environment parity** to reduce surprises
