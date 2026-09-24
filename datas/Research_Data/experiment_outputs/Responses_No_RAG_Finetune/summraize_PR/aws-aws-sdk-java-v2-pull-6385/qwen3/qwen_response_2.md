Here's a concise summary of the GitHub PR:

**Core Issue**  
The SDK's codegen for endpoint interceptors incorrectly assumed endpoint parameters *always* contain a `region` member. This caused compilation failures when endpoint rulesets didn't define a `region` parameter (which is allowed per AWS service models).

**Fix**  
- **Prefer endpoint params' `region`** if defined (for backwards compatibility).  
- **Fallback to client region** from execution attributes if `region` is missing.  
- Added safe null-checking logic in `EndpointResolverInterceptorSpec.java`.

**Key Changes**  
1. Updated codegen logic to conditionally use `endpointParams.region()` or `executionAttributes.AWS_REGION` (via `regionExpr`).
2. Added **two new test cases**:
   - `endpointResolverInterceptorClassWithSigv4aMultiAuth_withRegionParameter` (tests when `region` exists).
   - `endpointResolverInterceptorClassWithSigv4aMultiAuth_noRegionParameter` (tests fallback to client region).
3. Generated test output files verify the correct region resolution path.

**Impact**  
- **Bugfix** (not a feature), resolving compilation failures in SDK clients using endpoint rulesets without `region` parameters.
- Maintains backwards compatibility with existing service models.
- Added required changelog entry (type: `bugfix`).

**Why It Matters**  
AWS service models *don't require* a `region` parameter in endpoint rulesets. The fix ensures SDK codegen works correctly for all service models, avoiding broken builds.  

*No new functionality added — only a safety net for existing SDK behavior.*