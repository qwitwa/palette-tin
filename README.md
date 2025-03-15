# PaletteTin

Palette Tin is a Krita Docker plugin designed to help with color mixing and palette management. Inspired by the Art Academy mixing interface, it aims to make painting more fun by reducing the need for micromanaging color picking and mixing outside the canvas.

## Why PaletteTin?

PaletteTin is built to enhance your painting workflow by:
- Make color mixing a satisfying and fun experience
- Making color mixing more intuitive.
- Avoiding micromanagement in color selection.
- Embedding your palette history within the document for easy reference.

## Demo

<p align="center">
  <img src="/readme-assets/palletTin-help.png" />
</p>

https://github.com/user-attachments/assets/651b54da-58e7-4a2f-8bff-e40c80116dfc

## Features

- **Multiple Color Mixing Modes:**
  - **Spectral:** Uses Kubelka-Munk theory (via [spectral.js](https://github.com/rvanwijnen/spectral.js))
  - **Weighted Average:** Mixes two colors using a weighted average.
  - **Hybrid:** Combines spectral (60%) and weighted average (40%) for slightly less saturated results.
  - **Overlay:** Blends colors based on lightness (Screen if light, Multiply if dark), useful when highly saturated mixes are needed.
  - **Sat Val:** Transfers saturation and value from the foreground while preserving the hue.
  - **Sat Val okhsl:** Transfers okhsl saturation and lightness, retaining perceptual values. (via [Björn Ottosson OKHSL](https://bottosson.github.io/misc/ok_color.h))
- **Palette Management:**
  - Saves the palette directly into the working document as a note.
  - Stores palettes for later use in other documents using a custom format.
- **Extended Mixing Options:**
  - Mix paint outside the canvas.
  - Includes a scratchpad for testing colors off-canvas.

## Installation

### Method 1 (easiest)

Open Krita go to `Tools > Scripts > Import Python Plugin From Web` and paste the following URL.

https://github.com/josepablo-espinoza/palette-tin/releases/latest/download/palette-tin.zip

### Method 2

1. **Download latest release zip**:

  https://github.com/josepablo-espinoza/palette-tin/releases/latest/download/palette-tin.zip

2. **Upload the plugin into Krita**: 

  Open Krita go to `Tools > Scripts > Import Python Plugin From File` and load the zip file.

3. **Restart Krita**: If Krita was running, restart it to load the new Docker.

4. **Activate the Docker**: 
  Go to `Settings > Dockers > Palette Tin` to activate the Docker in Krita.

## Usage

- **Mixing:** Select a mixing mode from the dropdown, adjust the mix rate, and click on the palette grid to mix colors.
- **Scratchpad:** Test and experiment with colors off the main canvas.
- **Palette Storage:** Save and load your palettes directly within the document for future use.

## TODO

- KPL palettes support: after saving, a reboot is needed for the palettes to appear.
- Improve the default palette.
- Improve the demo video.
- Custom icons.

## IDEAS

- Add an opacity slider to simulate the effect of a thinning agent in real-life painting.
