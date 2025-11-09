Here's a concise summary of the GitHub PR:

**Problem**:  
The SDK's code generator assumed endpoint parameters *always* contained a `region` member, but AWS service rulesets aren't required to include this parameter. When missing, compilation failed.

**Fix**:  
- **Check for `region` in endpoint params first** (for backwards compatibility).  
- **Fallback to client region** from `executionAttributes` if `region` is absent.  
- Added robust handling to prevent compilation failures.

**Key Changes**:  
1. Modified `EndpointResolverInterceptorSpec.java` to dynamically check for `region` in endpoint params.  
2. Added **two new tests**:  
   - One with `region` parameter (existing behavior).  
   - One *without* `region` parameter (new fallback behavior).  
3. Updated changelog with a clear bugfix description.  

**Type**:  
✅ **Bugfix** (non-breaking, maintains backwards compatibility).  

**Why it matters**:  
Ensures SDK generation succeeds for all service rulesets (even those without `region`), resolving a critical compilation blocker. Tests validate both scenarios work as expected.  

*No new features added; purely a fix for a missing safety check.*