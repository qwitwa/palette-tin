# def getColorName(hue, saturation, value):
# Color Naming System (CNS) 
#  todo use a QColor
def getColorName(hsv):
    hue = hsv[0]
    saturation = hsv[1]
    value = hsv[2]
    # Hue ranges
    hueNamesOld = [
        (355, 360, 'Red'), (0, 10, 'Red'), (11, 20, 'Red-Orange'),
        (21, 40, 'Orange-Brown'), (41, 50, 'Orange-Yellow'),
        (51, 60, 'Yellow'), (61, 80, 'Yellow-Green'),
        (81, 140, 'Green'), (141, 169, 'Green-Cyan'),
        (170, 200, 'Cyan'), (201, 220, 'Cyan-Blue'),
        (221, 240, 'Blue'), (241, 280, 'Blue-Magenta'),
        (281, 320, 'Magenta'), (321, 330, 'Magenta-Pink'),
        (331, 354, 'Pink-Red')
    ]

    hueNames = [
        (0, 14, 'Red'),
        (15, 29, 'Vermilion'),
        (30, 44, 'Orange'),
        (45, 59, 'Amber'),
        (60, 74, 'Yellow'),
        (75, 89, 'Lime'),
        (90, 104, 'Chartreuse'),
        (105, 119, 'Ddahal'),
        (120, 134, 'Green'),
        (135, 149, 'Erin'),
        (150, 164, 'Spring'),
        (165, 179, 'Gashyanta'),
        (180, 194, 'Cyan'),
        (195, 209, 'Capri'),
        (210, 224, 'Azure'),
        (225, 239, 'Cerulean'),
        (240, 254, 'Blue'),
        (255, 269, 'Volta'),
        (270, 284, 'Violet'),
        (285, 299, 'Llew'),
        (300, 314, 'Magenta'),
        (315, 329, 'Cerise'),
        (330, 344, 'Rose'),
        (345, 358, 'Crimson'),
        (359, 360, 'Red')
    ]

    # Value (brightness) adjectives
    valueAdjectives = [
        (0, 9, 'very dark'), (10, 25, 'dark'),
        (26, 55, 'moderate'), (56, 80, 'light'),
        (81, 100, 'very light')
    ]

    # Saturation adjectives
    saturationAdjectives = [
        (0, 9, 'whitish'), (10, 25, 'pale'),
        (26, 55, 'dim'), (56, 80, 'brilliant'),
        (81, 100, 'vivid')
    ]

    # Find the hue name
    hueName = 'Gray'
    for lower, upper, name in hueNames:
        if lower <= hue <= upper:
            hueName = name
            break

    # Find the value adjective
    valuePercentage = value * 100 // 255
    valueAdj = None
    for lower, upper, adj in valueAdjectives:
        if lower <= valuePercentage <= upper:
            valueAdj = adj
            break

    # Find the saturation adjective
    saturationPercentage = saturation * 100 // 255
    saturationAdj = None
    for lower, upper, adj in saturationAdjectives:
        if lower <= saturationPercentage <= upper:
            saturationAdj = adj
            break

    # Special cases for achromatic colors
    if saturationPercentage <= 25 and valuePercentage <= 20:
        return f"blackish {hueName}"
    elif saturationPercentage <= 10 and valuePercentage >= 90:
        return f"whitish {hueName}"
    elif saturationPercentage < 20 and 20 < valuePercentage < 90:
        return f"grayish {hueName}"

    # Case 2: Value adjective + Saturation adjective + Hue name
    return f"{valueAdj} {saturationAdj} {hueName}"

# colorName = getColorName([33.4, 27, 33])
# colorName = getColorName([0, 0, 78])
# colorName = getColorName([332, 72, 91])
# colorName = getColorName([33.4, 27, 33])
# print(colorName)