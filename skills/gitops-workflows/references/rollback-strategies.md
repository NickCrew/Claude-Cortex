# Rollback Strategies

## Git-Based Rollback

**Revert commit:**
```bash
# Find problematic commit
git log --oneline

# Revert specific commit
git revert abc123
git push origin main

# ArgoCD/Flux automatically syncs rollback
```

**Rollback to previous tag:**
```bash
# Production currently on v1.2.3
# Rollback to v1.2.2
git checkout production
git reset --hard v1.2.2
git push --force origin production

# Update Application targetRevision
kubectl patch application frontend \
  -n argocd \
  --type merge \
  -p '{"spec":{"source":{"targetRevision":"v1.2.2"}}}'
```

## ArgoCD Rollback

**History and rollback:**
```bash
# View deployment history
argocd app history frontend

# Rollback to specific revision
argocd app rollback frontend 5

# Rollback to previous revision
argocd app rollback frontend
```

**Automatic rollback:**
```yaml
# Rollout with automatic rollback
apiVersion: argoproj.io/v1alpha1
kind: Rollout
spec:
  strategy:
    canary:
      analysis:
        templates:
        - templateName: success-rate
        startingStep: 1

      # Auto-rollback on analysis failure
      abortScaleDownDelaySeconds: 30
```

## Flux Rollback

**Suspend automation:**
```bash
# Suspend Kustomization
flux suspend kustomization frontend

# Manually rollback Deployment
kubectl rollout undo deployment/frontend -n production

# Resume after validation
flux resume kustomization frontend
```
