# Workflow: Building a slide deck in Figma

## Phase 1: Setup

### 1.1 Get user info
```javascript
// Always start by checking who's logged in and which workspace to use
Figma:whoami
```
Use the `planKey` from the response for file creation (e.g. `team::929068967373356657`).

### 1.2 Create the target file
```javascript
Figma:create_new_file({
  editorType: "design",
  fileName: "Deck Name Here",
  planKey: "team::929068967373356657"
})
```
Save the returned `file_key` — you'll use it for every subsequent operation.

### 1.3 The slide grid

All slides in the Slide Library align to a canonical grid. When creating new slides or modifying layouts, respect this grid:

- **12 columns**, 32px gutters, 56px offset (margin), stretch alignment
- **6 rows**, 0px gutters, 56px offset (margin), stretch alignment

The offset and gutter values are bound to MW spacing variables:
- Offset (56px) → spacing token `13` (key: `15603ca8bb5d267810d1d68a95857f4166e0211b`)
- Column gutter (32px) → spacing token `10` (key: `5f5e47d3132facac8c653b5db58bfa2e1fbe9964`)
- Row gutter (0px) → spacing token `0` (key: `17777977289bf1c4697989f1be95a44f17332c03`)

This grid produces a 1808px content area (1920 - 56×2) divided into 12 columns. Common column spans: 4 columns ≈ content card width, 6 columns = half-width, 12 columns = full-width.

To apply the grid to a new slide frame via Plugin API:
```javascript
slide.layoutGrids = [
  {
    pattern: "COLUMNS",
    visible: false,
    color: { r: 0.13, g: 0.95, b: 0.61, a: 0.11 },
    alignment: "STRETCH",
    gutterSize: 32,
    count: 12,
    offset: 56
  },
  {
    pattern: "ROWS",
    visible: false,
    color: { r: 1, g: 0.49, b: 0.43, a: 0.21 },
    alignment: "STRETCH",
    gutterSize: 0,
    count: 6,
    offset: 56
  }
];
```

### 1.4 Study the source content
If the user provides a source deck (Figma URL, uploaded file, or text content):
- Use `Figma:get_screenshot` on each slide to understand the content
- Use `Figma:get_metadata` to understand structure
- Read any uploaded documents or text to extract the content

---

## Phase 2: Outline and plan

**Before building anything, produce a complete deck outline and present it to the user for approval.**

### 2.1 Build the outline

Using the source content, map every slide to a layout from `slide-library-catalog.md`. For each slide, specify:

1. **Slide number and layout name** (e.g. "Slide 3 — 3 Column/Offer")
2. **Rough content summary** — what text goes where (headline, body, card content, etc.)
3. **Visual elements** — images, icons, charts, graphs, vectors, or decorative elements needed
4. **Notes** — anything the user should know (e.g. "needs client logo", "chart data TBD", "pull quote from brief")

Format the outline as a numbered list so the user can scan it quickly and flag changes before you start building.

Example format:
```
## Deck Outline: [Deck Name]

1. **Title Page/Wide Pane** — "Barnabas: A Formation Experience" / MW logo / Circles cover graphic
2. **Entry Page** — "For over 12 years, Midwestern has partnered with faith-based organizations..."
3. **3 Column/Offer** — Three service pillars: Scoped Projects, Embedded Teams, Recruiting
   - Each card: title + description + bullet list
   - Icons: concentric circles, embedded layers, dot grid
4. **Graph** — Q4 ad campaign performance / chartreuse growth curve / overflow task list on right
   - Chart data: Nov → Dec → Jan progression
   - Will need to detach vector curve for custom path
5. ...
```

### 2.2 Present and confirm

Show the outline to the user. Wait for approval or changes before proceeding. If the user adjusts slide order, swaps layouts, or changes content — update the outline first, then begin building.

**Do not start importing slides until the user confirms the outline.**

---

## Phase 3: Build slide-by-slide

### 3.1 One slide at a time

For each slide in the confirmed outline, execute this sequence:

1. **Import** the layout component
2. **Position** the slide (vertical stacking at 1200px intervals)
3. **Populate** all text content for that slide
4. **Adjust** any visual elements (charts, icons, images) for that slide
5. **Verify** with a screenshot if needed
6. **Move to the next slide**

Do NOT batch-import all slides first and populate later. The slide should be fully built before moving on.

### 3.2 Import pattern

```javascript
// Import and position one slide
var comp = await figma.importComponentByKeyAsync("COMPONENT_KEY_HERE");
var instance = comp.createInstance();
instance.name = "01_slide_name";
instance.x = 0;
instance.y = SLIDE_INDEX * 1200; // 0, 1200, 2400, 3600...
```

**Do not batch more than 1 import per `use_figma` call for reliability.** Import one, populate it, then import the next.

### 3.3 Vertical stacking
Arrange slides at y intervals of 1200 (1080px slide height + 120px gap):
- Slide 1: y = 0
- Slide 2: y = 1200
- Slide 3: y = 2400
- etc.

### 3.4 Font swap pattern (REQUIRED per slide)
TT Hoves is the MW brand font but is NOT available to the Figma Plugin API (it's a local font, not a Google Font, and the workspace is on the Professional plan — not Organization/Enterprise which supports uploaded fonts).

**Always swap to DM Sans before editing text:**

```javascript
await figma.loadFontAsync({ family: "DM Sans", style: "Regular" });
await figma.loadFontAsync({ family: "DM Sans", style: "Bold" });
await figma.loadFontAsync({ family: "DM Sans", style: "Medium" });

function setText(node, text) {
  if (!node || node.type !== "TEXT") return;
  try {
    var style = "Regular";
    if (node.fontName && node.fontName.style) {
      if (node.fontName.style.indexOf("Bold") > -1) style = "Bold";
      else if (node.fontName.style.indexOf("Medium") > -1) style = "Medium";
    }
    node.fontName = { family: "DM Sans", style: style };
    node.characters = text;
  } catch(e) {}
}
```

**Tell the user** they'll need to select all text and reapply TT Hoves text styles from the DS library as a final step.

### 3.5 Finding text nodes
Slide Library components have consistent naming patterns for common elements:
- `"Page Number"` — footer page number (16px)
- `"Presentation Title"` — footer deck name (16px)
- `"Section Title"` — footer section label (16px)

For other text, find by font size or inspect the node tree:
```javascript
var slide = page.findOne(n => n.name === "slide_name");
var texts = slide.findAll(n => n.type === "TEXT");
// Log IDs, font sizes, and current content to map what goes where
```

### 3.6 Footer update pattern
Every slide has a Deck Crawler footer. Update all three fields:
```javascript
function updateFooter(slide, pageNum, section) {
  var pn = slide.findOne(n => n.name === "Page Number");
  var pt = slide.findOne(n => n.name === "Presentation Title");
  var st = slide.findOne(n => n.name === "Section Title");
  if (pn) setText(pn, pageNum);
  if (pt) setText(pt, "Deck Title");
  if (st) setText(st, section);
}
```

---

## Phase 4: Token binding

### 4.1 Import MW Design System variables
```javascript
const varBlack = await figma.variables.importVariableByKeyAsync("2006036f22cccc77a7c5abe5f8ab4e20f0d0e8cf");
const varWhite = await figma.variables.importVariableByKeyAsync("898219b2f7dd9ff996ea2d90d26243b8cfd4e51f");
const varBlue = await figma.variables.importVariableByKeyAsync("85c7a4b71e4e503d292c40518035ad689a701f1f");
const varGreen = await figma.variables.importVariableByKeyAsync("ba8ecbc4bf1d8738735e19f393eaa5261d2948b0");
const varDarkGray = await figma.variables.importVariableByKeyAsync("6abe8a8b2c4c540171c9d4795b7dc5305d019b4f");
const varMedGray = await figma.variables.importVariableByKeyAsync("b85ab2bd4956b0342b5c9dd7f982eda2f23f10c0");
```

### 4.2 Bind fills to variables
```javascript
function bindFillToVar(node, variable, opacity) {
  var fills = JSON.parse(JSON.stringify(node.fills));
  if (fills.length === 0) {
    fills = [{ type: 'SOLID', color: { r: 0, g: 0, b: 0 }, opacity: opacity || 1 }];
  }
  fills[0] = figma.variables.setBoundVariableForPaint(fills[0], 'color', variable);
  if (opacity !== undefined) fills[0].opacity = opacity;
  node.fills = fills;
}
```

### 4.3 Import text styles
```javascript
const tsDisplayLg = await figma.importStyleByKeyAsync("94825b96d798b39cfa724b138c2d22832ca19580");
const tsBodyLg = await figma.importStyleByKeyAsync("285090d2e1d66ec51664592ce2ca63528d6140e3");
const tsCaption = await figma.importStyleByKeyAsync("1e4197592aeb4537d3f363dfd2bf773a7e7d0f3c");
// Apply: node.textStyleId = tsDisplayLg.id;
```

### 4.4 Import the MW mark
```javascript
const markComp = await figma.importComponentSetByKeyAsync("05c1282e87b7374891a30c4b8fdc11c6153927de");
// Pick the default variant from the set
const defaultVariant = markComp.children[0];
const markInstance = defaultVariant.createInstance();
// To make white on dark bg, override fills on children:
function setWhite(node) {
  if ('fills' in node) {
    var fills = JSON.parse(JSON.stringify(node.fills));
    if (fills.length > 0 && fills[0].type === 'SOLID') {
      fills[0].color = { r: 246/255, g: 247/255, b: 254/255 };
      delete fills[0].boundVariables;
      node.fills = fills;
    }
  }
  if ('children' in node) {
    for (var j = 0; j < node.children.length; j++) setWhite(node.children[j]);
  }
}
```

---

## Phase 5: Cleanup and handoff

### 5.1 Remove duplicates
After all operations, scan for duplicate frames at the same position:
```javascript
var allFrames = page.children;
// Check for frames with the same name and y position — remove duplicates
```

### 5.2 Verify with screenshots
Take screenshots of key slides to confirm content:
```javascript
Figma:get_screenshot({ fileKey: "...", nodeId: "..." })
```

### 5.3 Tell the user what to do manually
Always list remaining manual steps:
1. Select all text → reapply TT Hoves text styles from DS library
2. Drop images into any image placeholder slots
3. Review and adjust any content that couldn't be edited via API
