### Code Review Summary

- **Readability & Consistency**  
  - Use 4-space indentation and consistent formatting.  
  - Improve function/variable names for clarity (e.g., `fetch_resource` → `fetch_resource_details`).  

- **Naming Conventions**  
  - `hash` is clear, but `fetch_resource` lacks specificity.  
  - `download_file` and `batch_fetch` could be more descriptive.  

- **Software Engineering Standards**  
  - Default `use_cache=True` for `fetch_resource` is unclear.  
  - `wait_until_ready` lacks error handling and edge case coverage.  

- **Logic & Correctness**  
  - `wait_until_ready` assumes all URLs are ready, but fails on failures.  
  - `print_summary` lacks error handling for invalid results.  

- **Performance & Security**  
  - Chunk size in `download_file` is arbitrary (1234).  
  - MD5 checksums are insecure for verification.  

- **Documentation & Testing**  
  - Missing docstrings for most functions.  
  - No tests for edge cases (e.g., invalid URLs, redirects).  

---

### Improvement Suggestions  
1. **Rename Functions**:  
   - `fetch_resource` → `fetch_resource_details`.  
   - `download_file` → `download_resource`.  

2. **Clarify Defaults**:  
   - Set `use_cache=False` as default for `fetch_resource`.  

3. **Add Error Handling**:  
   - `wait_until_ready` should return `False` on failures.  

4. **Improve Chunk Size**:  
   - Use `1024` for `download_file` to balance performance and memory.  

5. **Enhance Security**:  
   - Replace MD5 with SHA-256 for checksums.  

6. **Add Docstrings**:  
   - Docs for `fetch_and_verify`, `batch_fetch`, and `main`.  

7. **Refactor Duplicates**:  
   - Extract shared logic (e.g., `headers` setup) into helper functions.