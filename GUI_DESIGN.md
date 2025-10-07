# GUI Design Documentation

## Application Window

```
┌─────────────────────────────────────────────────────────┐
│              Simple Image Converter                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ╔═══════════════ Input File ═════════════════╗         │
│  ║  /path/to/image.jpg                [Browse...]       │
│  ╚═══════════════════════════════════════════════════╝  │
│                                                          │
│  ╔═══════ Output File (Optional) ════════════╗          │
│  ║  Auto (same as input location)     [Browse...]       │
│  ╚═══════════════════════════════════════════════════╝  │
│                                                          │
│  ╔═══════════ Output Format ═══════════════╗            │
│  ║  Convert to: [png          ▼]                        │
│  ╚═══════════════════════════════════════════════════╝  │
│                                                          │
│  ╔════════ Conversion Parameters ═══════════╗           │
│  ║                                                       │
│  ║  Quality (1-100):                                    │
│  ║  [──────────────●────────] 95                        │
│  ║                                                       │
│  ║  Compression (0-9):                                  │
│  ║  [──────●───────────────] 6                          │
│  ║                                                       │
│  ║  ☐ Resize Image                                      │
│  ║     Width: [800  ] Height: [600  ]                   │
│  ║     ☑ Maintain aspect ratio                          │
│  ║                                                       │
│  ║  ℹ Format-specific information appears here          │
│  ║                                                       │
│  ╚═══════════════════════════════════════════════════╝  │
│                                                          │
│              ┌──────────────┐                            │
│              │   Convert    │                            │
│              └──────────────┘                            │
│                                                          │
├─────────────────────────────────────────────────────────┤
│ Status: Ready                                            │
└─────────────────────────────────────────────────────────┘
```

## Window Specifications

- **Size**: 700x650 pixels
- **Resizable**: No (fixed layout)
- **Title**: "Simple Image Converter"

## UI Components

### 1. Title
- **Type**: Label
- **Text**: "Simple Image Converter"
- **Font**: Arial, 18pt, Bold
- **Alignment**: Center

### 2. Input File Section
- **Type**: LabelFrame
- **Label**: "Input File"
- **Components**:
  - Label showing selected file path
  - Browse button (opens file dialog)

### 3. Output File Section
- **Type**: LabelFrame
- **Label**: "Output File (Optional)"
- **Components**:
  - Label showing output path or "Auto"
  - Browse button (opens save dialog)

### 4. Output Format Section
- **Type**: LabelFrame
- **Label**: "Output Format"
- **Components**:
  - "Convert to:" label
  - Dropdown/Combobox with format options

### 5. Conversion Parameters Section
- **Type**: LabelFrame
- **Label**: "Conversion Parameters"
- **Components**:
  
  #### Quality Slider
  - Range: 1-100
  - Default: 95
  - Visible for: JPEG, WebP, HEIF/HEIC
  
  #### Compression Slider
  - Range: 0-9
  - Default: 6
  - Visible for: PNG
  
  #### Resize Options
  - Checkbox: "Resize Image"
  - Width input field (disabled by default)
  - Height input field (disabled by default)
  - Checkbox: "Maintain aspect ratio" (disabled by default)
  
  #### Format Info
  - Label showing format-specific information
  - Dynamic based on selected format

### 6. Convert Button
- **Type**: Button
- **Text**: "Convert"
- **Color**: Green background (#4CAF50), White text
- **Size**: Large (padx=30, pady=10)
- **Position**: Center bottom

### 7. Status Bar
- **Type**: Label
- **Position**: Bottom of window
- **Shows**: Current operation status

## Color Scheme

- **Background**: Default system color (light gray/white)
- **LabelFrames**: Light gray borders
- **Convert Button**: 
  - Background: #4CAF50 (green)
  - Foreground: White
- **Info Text**: Blue (#0000FF)
- **Error Text**: Red (in message boxes)

## User Flow

```
┌─────────────┐
│   Start     │
└──────┬──────┘
       │
       v
┌─────────────────┐
│ Select Input    │◄─── Browse button opens file dialog
│ File            │     Supports: png, jpg, gif, bmp, tiff,
└──────┬──────────┘              webp, heif, heic, svg, psd
       │
       v
┌─────────────────┐
│ Choose Output   │◄─── Dropdown shows available formats
│ Format          │
└──────┬──────────┘
       │
       v
┌─────────────────┐
│ Adjust          │◄─── Controls update based on format
│ Parameters      │     - Quality for JPEG/WebP
└──────┬──────────┘     - Compression for PNG
       │                - Resize options
       │
       v
┌─────────────────┐
│ (Optional)      │◄─── Browse button opens save dialog
│ Select Output   │     If skipped, saves to input location
│ Location        │
└──────┬──────────┘
       │
       v
┌─────────────────┐
│ Click Convert   │
└──────┬──────────┘
       │
       v
┌─────────────────┐
│ Processing...   │◄─── Status bar shows "Converting..."
└──────┬──────────┘
       │
       v
┌─────────────────┐
│ Success Dialog  │◄─── Shows output file path
│ or Error        │
└──────┬──────────┘
       │
       v
┌─────────────────┐
│ Ready for Next  │
│ Conversion      │
└─────────────────┘
```

## Dynamic Behavior

### Format Selection

When a format is selected, the UI updates to show relevant controls:

| Format | Quality | Compression | Notes |
|--------|---------|-------------|-------|
| PNG    | Hidden  | Shown       | Shows compression info |
| JPEG   | Shown   | Hidden      | Shows quality info |
| WebP   | Shown   | Hidden      | Shows quality info |
| GIF    | Hidden  | Hidden      | Palette conversion note |
| BMP    | Hidden  | Hidden      | No compression |
| TIFF   | Hidden  | Hidden      | Multi-page support info |
| ICO    | Hidden  | Hidden      | Icon format info |
| EPS    | Hidden  | Hidden      | Vector format info |
| PDF    | Hidden  | Hidden      | Document format info |
| HEIF   | Shown   | Hidden      | Requires library note |

### Resize Checkbox

When "Resize Image" is checked:
- Width input: Enabled
- Height input: Enabled
- "Maintain aspect ratio" checkbox: Enabled

When unchecked, all three are disabled.

### Validation

- **Input file**: Must be selected before conversion
- **Output format**: Always has a default selection (png)
- **Width/Height**: Validated as integers > 0 if resize is enabled
- **Quality**: Constrained to 1-100 by slider
- **Compression**: Constrained to 0-9 by slider

## Error Handling

All errors show message boxes with clear explanations:

1. **No input file**: "Please select an input file"
2. **File not found**: "Input file does not exist"
3. **Unsupported format**: Details about missing library
4. **Conversion error**: Shows exception message
5. **Invalid dimensions**: "Invalid width/height values"

## Success Feedback

On successful conversion:
- Message box: "Image converted successfully!"
- Shows output file path
- Status bar: "Conversion successful!"
- Output file field resets to "Auto"
- Ready for next conversion

## Accessibility

- Tab navigation supported
- Keyboard shortcuts work
- Clear visual feedback for all actions
- Tooltips could be added in future versions
- High contrast mode compatible
