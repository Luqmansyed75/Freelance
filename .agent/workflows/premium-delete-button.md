---
description: How to add a premium circular SVG dustbin/delete button to a Streamlit app
---

# Premium SVG Delete Button Workflow

When the user asks to add the "premium delete button" (or `/premium-delete-button`), follow these exact steps to inject a Dribbble-style circular SVG dustbin button directly into Streamlit smoothly.

### 1. Python Code Implementation
The underlying button must be a native Streamlit button with `type="primary"` (to isolate its CSS from standard secondary buttons). You must hide the text "Delete" strictly via CSS, not by passing an empty string to Streamlit (which breaks button layout constraints).

```python
# The button must have type="primary" and SOME text so it calculates width properly before CSS hides it
if st.button("Delete", key=f"del_{item_id}", type="primary", help="Delete Item"):
    delete_function(item_id)
```

### 2. CSS Injection
Inject the following CSS using `st.markdown("<style>...</style>", unsafe_allow_html=True)`.

```css
/* Premium Circular Dustbin Button */
div[data-testid="stButton"] button[kind="primary"] {
    background: #ea2b2b !important;
    border-radius: 50% !important;
    width: 58px !important;
    height: 58px !important;
    padding: 0 !important;
    border: none !important;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 6px 15px rgba(234, 43, 43, 0.3) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
}

div[data-testid="stButton"] button[kind="primary"]:hover {
    transform: translateY(-2px) scale(1.05);
    box-shadow: 0 10px 25px rgba(234, 43, 43, 0.5) !important;
}

/* Hide the native text */
div[data-testid="stButton"] button[kind="primary"] p {
    display: none !important;
}

/* Inject the SVG strictly centered using absolute position to prevent Streamlit margin interference */
div[data-testid="stButton"] button[kind="primary"]::after {
    content: '';
    width: 26px;
    height: 26px;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'%3E%3Cpath d='M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z'/%3E%3C/svg%3E");
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    display: block;
}
```

### 3. Verification
Ensure the SVG is rendering properly as `fill='white'` inside a valid `.svg` data wrapper, and that it is fully centered. Ensure no other primary buttons in the application are inadvertently affected.
