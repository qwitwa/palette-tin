from PyQt5.QtGui import QValidator

class FloatValidator(QValidator):
    def validate(self, inputStr, pos):
        if not inputStr:
            return (QValidator.Intermediate, inputStr, pos)
        
        try:
            float(inputStr)
            return (QValidator.Acceptable, inputStr, pos)
        except ValueError:
            return (QValidator.Invalid, inputStr, pos)
        
class IntValidator(QValidator):
    def validate(self, inputStr, pos):
        if not inputStr:
            return (QValidator.Intermediate, inputStr, pos)
        
        try:
            int(inputStr)
            return (QValidator.Acceptable, inputStr, pos)
        except ValueError:
            return (QValidator.Invalid, inputStr, pos)