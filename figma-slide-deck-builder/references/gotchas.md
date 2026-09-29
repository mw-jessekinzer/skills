# Gotchas: Known pitfalls and solutions

Every issue documented here was encountered during real deck-building sessions. Read this when something unexpected happens.

---

## Font handling

### TT Hoves is not loadable via the Plugin API
**Problem**: TT Hoves is installed locally on the user's machine and visible in the Figma desktop app, but `figma.loadFontAsync({ family: "TT Hoves", style: "Regular" })` fails because the Plugin API (MCP) runs server-side and can only access Google Fonts and org-uploaded fonts.

**Cause**: The workspace is on the Professional plan. Custom font uploads to the workspace require the Organization or Enterprise plan.

**Solution**: Always swap text nodes to DM Sans before editing, then tell the user to reapply TT Hoves text styles manually after.

```javascript
// Pattern: swap font, then set text
var style = "Regular";
if (node.fontName.style.indexOf("Bold") > -1) style = "Bold";
node.fontName = { family: "DM Sans", style: style };
node.characters = "New text here";
```

**User instruction**: "Select all text → open the text styles panel → reapply the TT Hoves styles from the MW Design System library."

### Mixed fonts in a single text node
**Problem**: Some text nodes have `fontName` as a `Symbol` (mixed fonts) instead of an object, causing `node.fontName.style` to throw.

**Solution**: Always wrap font operations in try/catch and skip nodes that error.

---

## Component instances

### Text overrides don't persist on nested instances
**Problem**: You update text inside a component instance, the API returns success, but the text doesn't change in the file.

**Cause**: The text node is deeply nested inside sub-instances. Instance overrides only work for direct children or specifically exposed text properties.

**Solution**: Check if the edit actually took effect by re-reading the node's characters after setting them. If it didn't stick, note it as a manual edit for the user.

### Detach instances before editing vector paths
**Problem**: You try to modify a vector path (e.g., reshaping a chart curve) inside a component instance and either get an error or the change doesn't appear.

**Cause**: Vector paths inside instances are locked to the main component's definition.

**Solution**: Detach the instance first, then edit:
```javascript
var slide = page.findOne(n => n.name === "slide_name");
// Detach all nested instances
var instances = slide.findAll(n => n.type === "INSTANCE");
for (var i = 0; i < instances.length; i++) {
  try { instances[i].detachInstance(); } catch(e) {}
}
// Now vector paths are editable
```

### The old instance hiding the new frame
**Problem**: You detach an instance (creating a new frame), edit the frame, but the user still sees the old content.

**Cause**: `detachInstance()` creates a new frame but may leave the original instance in place at the same coordinates. The old instance renders on top, hiding the new frame.

**Solution**: After detaching, always check for and remove duplicates:
```javascript
var allFrames = page.children;
var seen = {};
var toRemove = [];
for (var i = 0; i < allFrames.length; i++) {
  var key = allFrames[i].name + "|" + allFrames[i].y;
  if (seen[key]) {
    // Keep the FRAME (detached), remove the INSTANCE (old)
    if (allFrames[i].type === "INSTANCE") toRemove.push(allFrames[i]);
    else if (seen[key].type === "INSTANCE") toRemove.push(seen[key]);
  }
  seen[key] = allFrames[i];
}
for (var j = 0; j < toRemove.length; j++) toRemove[j].remove();
```

---

## Importing components

### Batch imports cause timeouts
**Problem**: Importing 5+ components in a single `use_figma` call fails with a timeout error.

**Solution**: Import 2-3 components max per call. Split into multiple calls.

### Component keys may change
**Problem**: A component key from the catalog doesn't work.

**Cause**: The Slide Library was updated and components were recreated.

**Solution**: Query live keys from the Slide Library file:
```javascript
Figma:use_figma({
  fileKey: "9ZnOiRVkBQUbB1zRKcgkjF",
  code: `
    const page = figma.root.children.find(p => p.name === "Slides");
    const section = page.findOne(n => n.name === "Slides" && n.type === "SECTION");
    return JSON.stringify(section.children
      .filter(c => c.type === "COMPONENT")
      .map(c => ({ name: c.name, key: c.key })));
  `
})
```

---

## Vector path editing

### Updating chart curves
The `Layout/Graph` slide has two vector elements that form the chart:
1. **Vector 601** — the chartreuse stroke line (the visible curve)
2. **Rectangle 1** — the filled area under the curve (gradient fill)

Both must be updated to match when reshaping:

```javascript
// Stroke curve
var curve = figma.getNodeById("CURVE_ID");
curve.vectorPaths = [{
  windingRule: "NONZERO",
  data: "M 0 316 C 60 300 170 20 254 0 C 380 5 700 90 888 129"
}];

// Filled area (same curve + close to bottom)
var fill = figma.getNodeById("FILL_ID");
fill.vectorPaths = [{
  windingRule: "NONZERO",
  data: "M 0 316 C 60 300 170 20 254 0 C 380 5 700 90 888 129 L 888 328 L 0 328 L 0 316 Z"
}];
```

### Coordinate system for the graph
- Canvas: 888px wide × ~328px tall
- Y is inverted: y=0 is the TOP (max value), y=328 is the BOTTOM (zero)
- X-axis: 0 = leftmost label, 444 = middle label, 888 = rightmost label
- Map data values to Y: `y = height - (value / maxValue * height)`

---

## Color and token binding

### Variable binding syntax
```javascript
// This is NOT just setting a color — it binds to the published variable
fills[0] = figma.variables.setBoundVariableForPaint(fills[0], 'color', variable);
```

### Logo appears black on dark background
**Problem**: The imported MW logo component renders in Black (#010313), invisible on the dark slide background.

**Solution**: Walk the instance children and override all solid fills to White:
```javascript
function setWhite(node) {
  if ('fills' in node) {
    var fills = JSON.parse(JSON.stringify(node.fills));
    for (var i = 0; i < fills.length; i++) {
      if (fills[i].type === 'SOLID') {
        fills[i].color = { r: 246/255, g: 247/255, b: 254/255 };
        delete fills[i].boundVariables;
      }
    }
    node.fills = fills;
  }
  if ('children' in node) {
    for (var j = 0; j < node.children.length; j++) setWhite(node.children[j]);
  }
}
```

---

## Data visualization styling

When building or populating chart slides (Graph, Bar Chart, Gantt, etc.), apply these color and styling rules. They extend the MW visual language to data-heavy content.

### Color hierarchy
- **Background**: always `#010313` (MW Black) on standard slides. If a light-mode context is needed, use `#F6F7FE` (MW White). Never a colored background.
- **Primary data series**: foreground color — white on dark, black on light.
- **Highlight series**: MW Blue `#2237F1` for the single data series or element being emphasized. One highlight color per chart.
- **Callout accent**: MW Green `#C7FA50` for a single standout metric, annotation, or data label. Use at most once per chart — this is a "look here" signal, not a second data color.
- **Secondary / comparison data**: `#666666` or foreground at reduced opacity (~40-50%). Push it back so the primary series dominates.
- **Grid lines**: foreground at 8-10% opacity. They orient the eye, they don't compete with data. On dark slides, that's `rgba(246, 247, 254, 0.08)`.
- **Axes and labels**: muted color, small type (14-16px). These are reference, not content.

### Shape and fill rules
- **Sharp corners on everything** — bars, containers, tooltips, legend swatches. No border-radius. The MW system is angular.
- **No gradients.** Flat solid fills only. This applies to bar fills, area fills, and backgrounds.
- **Stroke-based decorative elements** — if you add reference lines, trend lines, or annotations, use thin white strokes consistent with the MW line-art language. Never filled decorative shapes.

### Applying in Figma Plugin API
Use the DS variable keys from `workflow.md § Token Binding` to bind chart element fills:
```javascript
// Primary data → MW White (on dark bg)
bindFillToVar(barNode, varWhite, 1);
// Highlight → MW Blue
bindFillToVar(highlightBar, varBlue, 1);
// Callout label → MW Green
bindFillToVar(calloutDot, varGreen, 1);
// Secondary data → MW White at reduced opacity
bindFillToVar(secondaryBar, varWhite, 0.4);
// Grid lines → MW White at 8% opacity
bindFillToVar(gridLine, varWhite, 0.08);
```

These rules keep charts feeling native to the slide system rather than pasted in from an external tool.

---

## MW slide visual language (DON'T violate these)

These rules come from studying the approved Slide Library. Violating them produces work that doesn't match the system:

1. **Background is always near-black #010313** — flat, no gradients, no color blocks
2. **Blue (#2237F1) appears as text accents only** — never as large filled areas or geometric shapes
3. **Green (#C7FA50) appears as tiny dot accents** — on timeline nodes, status indicators. Never as triangles, wedges, or filled regions
4. **Decorative elements are thin white stroke-only line art** — circles, arcs, dashed curves, field lines. Never filled polygons
5. **Cover Graphic is a contained rectangular pane** — not free-floating shapes
6. **Every slide has a Deck Crawler footer** — page number, presentation title, section title, M icon
7. **Typography is TT Hoves Regular** (not Bold) for everything — the DS text styles all use Regular weight
8. **Sentence case always** — never title case except proper nouns
