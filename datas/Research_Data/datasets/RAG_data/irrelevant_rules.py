"""Negative-control RAG corpus for the thesis ablation experiment.

These rules concern browser presentation and interaction design, not Python
program correctness. The corpus deliberately contains the same number of
documents as the production rule corpus so the negative control does not
silently change top-k capacity. It must only be selected explicitly with the
PRTHINKER_RAG_CORPUS=irrelevant environment setting.
"""

irrelevant_rule_docs = [
    """Use a consistent spacing scale for margins, padding, and gaps in visual layouts. Prefer a small set of reusable spacing tokens instead of unrelated pixel values so adjacent interface components retain a coherent rhythm.""",
    """Ensure foreground text and essential icons have sufficient colour contrast against their backgrounds. Validate both light and dark themes and do not rely on colour alone to communicate an interactive state.""",
    """Provide visible focus indicators for interactive browser controls. Keyboard users should be able to identify the currently focused element without depending on a mouse pointer or hover styling.""",
    """Keep heading levels hierarchical in rendered pages. Do not choose heading tags only for their default visual size, because assistive technology uses the document outline for navigation.""",
    """Supply meaningful alternative text for informative images and empty alternative text for purely decorative images. Avoid repeating a nearby caption word for word in the alternative text.""",
    """Design responsive layouts from content needs rather than from a single device width. Test narrow and wide viewports and allow text to reflow without horizontal scrolling.""",
    """Use typography tokens for font family, weight, size, and line height. Maintain a readable line length and avoid shrinking body text merely to fit more content above the fold.""",
    """Make interactive targets large enough for touch input and leave adequate separation between adjacent actions. Important actions should not require pixel-precise tapping on a mobile screen.""",
    """Label form fields persistently instead of using placeholder text as the only label. Error messages should identify the affected field and describe how the user can correct the value.""",
    """Preserve a clear visual distinction between primary, secondary, and destructive actions. Destructive actions should not be styled as the default path through a dialog.""",
    """Avoid layout shifts while web fonts, images, and asynchronous content load. Reserve expected dimensions so controls do not move away from the user's pointer during rendering.""",
    """Support reduced-motion preferences for non-essential animation. Transitions should communicate state change without becoming the only way that a change is perceivable.""",
    """Keep navigation labels concise and consistent across pages. The same destination should not appear under multiple unrelated names, and the current location should remain identifiable.""",
    """Use locale-aware formatting for dates, numbers, currency, and plural forms in user-facing interfaces. Do not concatenate translated fragments whose grammar depends on word order.""",
    """Provide useful empty, loading, success, and error states for data-driven interface regions. Each state should explain what happened and expose an appropriate next action when one exists.""",
    """Ensure modal dialogs manage focus correctly in the browser. Move focus into the dialog on open, keep keyboard focus within it, and restore focus to the initiating control on close.""",
    """Do not hide essential information behind hover-only interactions. Any content available on pointer hover should also be reachable through keyboard focus and touch interaction.""",
    """Use semantic table markup for genuinely tabular browser content. Associate header cells with data cells and provide a concise caption when the table's purpose is not obvious from context.""",
    """Maintain theme consistency for borders, shadows, corner radii, and elevation. Decorative effects should reinforce component hierarchy rather than introduce a separate visual vocabulary on each page.""",
]
