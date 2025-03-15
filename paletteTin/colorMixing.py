from .modules.spectraljs.spectral import * 
from PyQt5.QtGui import QColor
from .modules.oklab.oklab import *
import math

# Dictionary to store registered color mixer functions
# Use register_mixer decorator to add more mixing functions
# they must have baseColor [r,g,b] mixerColor [r,g,b] and mixRate
mixingList = {}

def register_mixer(name):
    """
    Decorator to register a color mixer function.
    
    Args:
        name (str): Name identifier for the mixer.
        
    Returns:
        function: Decorated function added to mixingList.
    """
    def decorator(func):
        mixingList[name] = func
        return func
    return decorator

@register_mixer("Spectral")
def spectral(baseColorRGB, mixerColorRGB, mixRate):
    """
    Mix two colors using the spectral method.
    
    Args:
        baseColorRGB (list): Base color [R, G, B].
        mixerColorRGB (list): Mixer color [R, G, B].
        mixRate (float): Mixing rate.
    
    Returns:
        list: Resulting mixed color.
    """
    return spectral_mix(baseColorRGB, mixerColorRGB, mixRate)

@register_mixer("Weighted average")
def mixWeightedAverage(baseColorRGB, mixerColorRGB, weight):
    """
    Mix two colors using a weighted average.
    
    Args:
        baseColorRGB (list): Base color [R, G, B].
        mixerColorRGB (list): Mixer color [R, G, B].
        weight (float): Weight for the mixer color (0 to 1).
        
    Returns:
        list: Resulting mixed color.
    """
    wc = 1 - weight  # Weight for the base color
    mixRed = int(wc * baseColorRGB[0] + weight * mixerColorRGB[0])
    mixGreen = int(wc * baseColorRGB[1] + weight * mixerColorRGB[1])
    mixBlue = int(wc * baseColorRGB[2] + weight * mixerColorRGB[2])
    return [mixRed, mixGreen, mixBlue]

@register_mixer("Hybrid")
def hybridMix(baseColorRGB, mixerColorRGB, mixRate):
    """
    Hybrid mix combining spectral and weighted average methods.
    
    Args:
        baseColorRGB (list): Base color [R, G, B].
        mixerColorRGB (list): Mixer color [R, G, B].
        mixRate (float): Mixing rate.
        
    Returns:
        list: Resulting mixed color.
    """
    hybridRate = 40  # Fixed percentage for hybrid mixing
    mixed1 = spectral_mix(baseColorRGB, mixerColorRGB, mixRate)
    mixed2 = mixWeightedAverage(baseColorRGB, mixerColorRGB, mixRate)
    return mixWeightedAverage(mixed1, mixed2, hybridRate / 100)

@register_mixer("Overlay")
def overlayMix(baseColorRGB, mixerColorRGB, mixRate):
    """
    Mix two colors using an overlay blend mode.
    
    Args:
        baseColorRGB (list): Base color [R, G, B].
        mixerColorRGB (list): Mixer color [R, G, B].
        mixRate (float): Mixing rate.
        
    Returns:
        list: Resulting mixed color.
    """
    def blendChannel(c1, c2):
        if c1 < 128:
            return (2 * c1 * c2) // 255
        else:
            return 255 - (2 * (255 - c1) * (255 - c2)) // 255

    mixedColor = [
        int(blendChannel(c1, c2) * mixRate + c1 * (1 - mixRate))
        for c1, c2 in zip(baseColorRGB, mixerColorRGB)
    ]
    return mixedColor

# @register_mixer("LERP")
def lerpBlend(baseColorRGB, mixerColorRGB, mixRate):
    """
    Mix two colors using linear interpolation (LERP).
    
    Args:
        baseColorRGB (list): Base color [R, G, B].
        mixerColorRGB (list): Mixer color [R, G, B].
        mixRate (float): Mixing rate.
        
    Returns:
        list: Resulting mixed color.
    """
    mixedColor = [
        int(c1 * (1 - mixRate) + c2 * mixRate)
        for c1, c2 in zip(baseColorRGB, mixerColorRGB)
    ]
    return mixedColor

# @register_mixer("Overlay Hybrid")
def hybridOverlayMix(baseColorRGB, mixerColorRGB, mixRate):
    """
    Hybrid mix combining spectral and overlay mixing methods.
    
    Args:
        baseColorRGB (list): Base color [R, G, B].
        mixerColorRGB (list): Mixer color [R, G, B].
        mixRate (float): Mixing rate.
        
    Returns:
        list: Resulting mixed color.
    """
    hybridRate = 40  # Fixed percentage for hybrid mixing
    mixed1 = spectral_mix(baseColorRGB, mixerColorRGB, mixRate)
    mixed2 = overlayMix(baseColorRGB, mixerColorRGB, mixRate)
    return mixWeightedAverage(mixed1, mixed2, hybridRate / 100)

@register_mixer("Sat Val")
def satValTransfer(baseColorRGB, mixerColorRGB, mixRate=None):
    """
    Transfer saturation and value from the mixer color to the base color,
    while preserving the base hue.
    
    Args:
        baseColorRGB (list): Base color [R, G, B].
        mixerColorRGB (list): Mixer color [R, G, B].
        mixRate: Not used.
        
    Returns:
        list: Resulting color with transferred saturation and value.
    """
    color = QColor(*baseColorRGB)
    color2 = QColor(*mixerColorRGB)
    
    # Set base color's saturation and value to that of the mixer color
    color.setHsv(color.hsvHue(), color2.hsvSaturation(), color2.value())
    
    return [color.red(), color.green(), color.blue()]

@register_mixer("Sat Val okhsl")
def hslTransfer(baseColorRGB, mixerColorRGB, mixRate=None):
    """
    Transfer perceptual lightness and saturation from the mixer color to the base color
    using Okhsl, while preserving the base color's chromatic components.
    
    Args:
        baseColorRGB (list): Base color [R, G, B] in 0-255.
        mixerColorRGB (list): Mixer color [R, G, B] in 0-255.
        mixRate: Not used.
        
    Returns:
        list: [R, G, B] in 0-255 base color with lightness transferred from mixer color.
    """
    baseRgb = RGB(baseColorRGB[0] / 255.0, baseColorRGB[1] / 255.0, baseColorRGB[2] / 255.0)
    mixerRgb = RGB(mixerColorRGB[0] / 255.0, mixerColorRGB[1] / 255.0, mixerColorRGB[2] / 255.0)
    
    # Convert sRGB to Okhsl
    baseHsl = srgbToOkhsl(baseRgb)
    mixerHsl = srgbToOkhsl(mixerRgb)
    
    # Transfer lightness and saturation from the mixer while preserving the base hue
    newHsl = HSL(baseHsl.h, mixerHsl.s, mixerHsl.l)
    
    # Convert back to sRGB
    newRgb = okhslToSrgb(newHsl)
    
    # Convert normalized RGB back to 0-255 with clamping
    r = round(clamp(newRgb.r, 0, 1) * 255)
    g = round(clamp(newRgb.g, 0, 1) * 255)
    b = round(clamp(newRgb.b, 0, 1) * 255)
    
    return [r, g, b]

@register_mixer("lightness okhsl")
def lightnessHslTransfer(baseColorRGB, mixerColorRGB, mixRate=None):
    """
    Transfer perceptual lightness and saturation from the mixer color to the base color
    using Okhsl, while preserving the base color's chromatic components.
    
    Args:
        baseColorRGB (list): Base color [R, G, B] in 0-255.
        mixerColorRGB (list): Mixer color [R, G, B] in 0-255.
        mixRate: Not used.
        
    Returns:
        list: [R, G, B] in 0-255 base color with lightness transferred from mixer color.
    """
    # Convert 0-255 input to normalized [0,1]
    baseRgb = RGB(baseColorRGB[0] / 255.0, baseColorRGB[1] / 255.0, baseColorRGB[2] / 255.0)
    mixerRgb = RGB(mixerColorRGB[0] / 255.0, mixerColorRGB[1] / 255.0, mixerColorRGB[2] / 255.0)
    
    # Convert sRGB to Okhsl
    baseHsl = srgbToOkhsl(baseRgb)
    mixerHsl = srgbToOkhsl(mixerRgb)
    
    # Transfer lightness and saturation from the mixer while preserving the base hue
    newHsl = HSL(baseHsl.h, baseHsl.s, mixerHsl.l)
    
    # Convert back to sRGB
    newRgb = okhslToSrgb(newHsl)
    
    # Convert normalized RGB back to 0-255 with clamping
    r = round(clamp(newRgb.r, 0, 1) * 255)
    g = round(clamp(newRgb.g, 0, 1) * 255)
    b = round(clamp(newRgb.b, 0, 1) * 255)
    
    return [r, g, b]