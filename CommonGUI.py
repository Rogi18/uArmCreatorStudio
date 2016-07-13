from PyQt5        import QtGui, QtCore, QtWidgets
import ast  # To check if a statement is python parsible, for evals
"""
This module is for storing general purpose widgets
"""

class LineTextWidget(QtWidgets.QFrame):
    """
    This puts line numbers on a QTextEdit widget
    """
    class NumberBar(QtWidgets.QWidget):

        def __init__(self, *args):
            QtWidgets.QWidget.__init__(self, *args)
            self.edit = None
            # This is used to update the width of the control.
            # It is the highest line that is currently visibile.
            self.highest_line = 0

        def setTextEdit(self, edit):
            self.edit = edit

        def update(self, *args):
            '''
            Updates the number bar to display the current set of numbers.
            Also, adjusts the width of the number bar if necessary.
            '''
            # The + 4 is used to compensate for the current line being bold.
            width = self.fontMetrics().width(str(self.highest_line)) + 4
            if self.width() != width:
                self.setFixedWidth(width)
            QtWidgets.QWidget.update(self, *args)

        def paintEvent(self, event):

            contents_y = self.edit.verticalScrollBar().value()
            page_bottom = contents_y + self.edit.viewport().height()
            font_metrics = self.fontMetrics()
            current_block = self.edit.document().findBlock(self.edit.textCursor().position())

            painter = QtGui.QPainter(self)

            line_count = 0
            # Iterate over all text blocks in the document.
            block = self.edit.document().begin()
            while block.isValid():
                line_count += 1

                # The top left position of the block in the document
                position = self.edit.document().documentLayout().blockBoundingRect(block).topLeft()

                # Check if the position of the block is out side of the visible
                # area.
                if position.y() > page_bottom: #gt; page_bottom:
                    break

                # We want the line number for the selected line to be bold.
                bold = False
                if block == current_block:
                    bold = True
                    font = painter.font()
                    font.setBold(True)
                    painter.setFont(font)

                # Draw the line number right justified at the y position of the
                # line. 3 is a magic padding number. drawText(x, y, text).
                painter.drawText(self.width() - font_metrics.width(str(line_count)) - 3, round(position.y()) - contents_y + font_metrics.ascent(), str(line_count))

                # Remove the bold style if it was set previously.
                if bold:
                    font = painter.font()
                    font.setBold(False)
                    painter.setFont(font)

                block = block.next()

            self.highest_line = line_count
            painter.end()

            QtWidgets.QWidget.paintEvent(self, event)

    def __init__(self, *args):
        QtWidgets.QFrame.__init__(self, *args)

        self.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Sunken)

        self.edit = QtWidgets.QTextEdit()
        self.edit.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.edit.setAcceptRichText(False)

        self.number_bar = self.NumberBar()
        self.number_bar.setTextEdit(self.edit)

        hbox = QtWidgets.QHBoxLayout(self)
        hbox.setSpacing(0)
        # hbox.setMargin(0)
        hbox.addWidget(self.number_bar)
        hbox.addWidget(self.edit)

        self.edit.installEventFilter(self)
        self.edit.viewport().installEventFilter(self)

    def eventFilter(self, object, event):
        # Update the line numbers for all events on the text edit and the viewport.
        # This is easier than connecting all necessary singals.
        if object in (self.edit, self.edit.viewport()):
            self.number_bar.update()
            return False
        return QtWidgets.QFrame.eventFilter(object, event)

    def setText(self, plainText):
        self.edit.setPlainText(plainText)

    def getTextEdit(self):
        return self.edit

    def getText(self):
        return self.edit.toPlainText()


class ScriptWidget(QtWidgets.QWidget):
    """This class is for making a text editor that will help you write python code"""

    documentation = "" +\
"""
    Using this scripting module, the possibilities are endless. You can directly inject python code into your program
without a hassle. You can use any of the libraries and modules that are built into this software, real time, and
without any extra modification. There are certain classes that are preloaded into this script that you can use.


Variables you have quick access to:
    robot
        You have full access to controlling the robot, using the Robot.py library that was built as a wrapper for
        a communication protocol.

        For source code on the Robot class, go to:
        https://github.com/apockill/RobotGUIProgramming/blob/master/Logic/Robot.py

    vision
        Using this module, you can easly and without hassle track objects that you have taught the software in the
        Resource manager, find their location real time, search for past "tracks" of the objects, and act based upon
        that information. You can clear tracked objects, add new ones, and generally use powerful premade computer
        vision functions that have been built into this software already.

        For source code on the Vision class, go to:
        https://github.com/apockill/RobotGUIProgramming/blob/master/Logic/Vision.py


    objectManager
        You can pull any "objects" that you have built using the Resource Manager. This means, for example,
        that you could request a Motion Recording and replay it, or request a Vision object and track it.

        For source code on the Object Manager class, go to:
        https://github.com/apockill/RobotGUIProgramming/blob/master/Logic/ObjectManager.py


Examples scripts using robot
    robot.setPos(x=0, y=15, z=15)   # This will set the robots position to XYZ(0, 15, 15)
    robot.setPos(x=0, y=15, z=15)   # Waits for robot to complete move before continuing
    robot.setPos(x=0)               # Will only set the x position, keeps the rest the same
    robot.setGripper(True)          # Turn on the pump. If false, it will deactivate the pump
    robot.setBuzzer(1500, 2)        # Play a tone through the robots buzzer. Parameters: Frequency, duration (seconds)
    robot.setSpeed(10)              # Sets speed for all future moves using robot.setPos. Speed set in cm/s
    robot.connected()               # Returns True if the robot is connected and working, False if not

    robot.getServoAngles()          # Returns the current angles of the robots servos in [servo0, servo1, servo2, servo3] format
    robot.getCurrentCoord()         # Returns the current coordinate of the robot in [x, y, z] format
    robot.getTipSensor()            # Returns True or False, if the tip sensor on the robot is being pressed or not
    robot.getMoving()               # Returns True if the robot is currently moving



Example scripts using vision
    # The first step of using vision is getting a trackable object. Make an object in Resources then access it by name here.
    trackableObject = objectManager.getObject("Ace of Spades")   # Get vision-compatible object by name using objectManager


    # The next step is to make sure vision is tracking the object. Usually this should be done in Initialization event.
    # Objects only stop being tracked when the script ends. Do this only once.
    vision.addPlaneTarget(trackableObject)


    # If the object is already being tracked and has been for a while, you can try using vision to search for it
    # This function returns how many frames ago the object was recognized, and a "tracked" object with some information
    frameID, trackedObject = vision.getObjectLatestRecognition(trackableObject)


    # If no object is found, the "trackedObject" will be None. Check if its None before continuing
    if trackedObject is None:
        # Handle the error here
        print("Object ", trackableObject.name, " was not recognized!")
        return

    # If the object was, in fact, found, then you can pull all sorts of information from it
    print(trackedObject.center)     # Prints a list [x, y, z] of the objects position in the cameras coordinate system
    print(trackedObject.rotation)   # Prints a list [xRotation, yRotation, zRotation] of rotation along each axis
    print(trackedObject.ptCount)    # Prints how many points the object was recognized with. More points = more accuracy


    # Here is another function for looking for tracked objects
    # This will search through the last 30 frames for trackableObject, and try to find a recognition with > 50 keypoints
    trackedObject = vision.searchTrackedHistory(trackable=trackableObject, maxAge=30, minPtCount=50)


"""
    minWidth  = 500
    minHeight = 600


    def __init__(self, previousCode, parent):
        super(ScriptWidget, self).__init__(parent)
        self.prompt = parent
        self.prompt.content.setContentsMargins(5, 5, 5, 5)
        self.prompt.setMinimumWidth(self.minWidth)
        self.prompt.setMinimumHeight(self.minHeight)

        # QtWidgets.QTextEdit().toP
        self.docText   = QtWidgets.QTextEdit()
        self.docBtn    = QtWidgets.QPushButton("Show Documentation")
        self.textEdit  = LineTextWidget()
        self.textEdit.setText(previousCode)

        self.hintLbl           = QtWidgets.QLabel("")  # Will give you warnings and whatnot
        self.initUI()

    def initUI(self):
        self.docText.setReadOnly(True)
        self.docText.setAcceptRichText(True)
        self.docText.setText(self.documentation)
        self.docText.setFixedWidth(900)
        self.docText.setFixedHeight(self.minHeight)
        # self.docText.set
        # self.docText.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.docBtn.setFixedWidth(150)
        self.docText.setHidden(True)

        bold = QtGui.QFont()
        bold.setBold(True)
        self.hintLbl.setFont(bold)



        self.docBtn.clicked.connect(self.showDocumentation)


        monospace = QtGui.QFont("Monospace")
        monospace.setStyleHint(QtGui.QFont.TypeWriter)
        self.textEdit.setFont(monospace)
        self.textEdit.setMinimumHeight(self.minHeight)
        self.textEdit.getTextEdit().textChanged.connect(self.verifyCode)
        self.docText.setFont(monospace)

        row1 = QtWidgets.QHBoxLayout()
        row2 = QtWidgets.QHBoxLayout()
        row3 = QtWidgets.QHBoxLayout()


        row1.addWidget(self.docBtn)
        row1.addStretch(1)

        row2.addWidget(self.textEdit)
        row2.addWidget(self.docText)
        row3.addWidget(self.hintLbl)


        mainVLayout = QtWidgets.QVBoxLayout()
        mainVLayout.addLayout(row1)
        mainVLayout.addLayout(row2)
        # mainVLayout.addStretch()
        mainVLayout.addLayout(row3)

        self.prompt.setMinimumWidth(600)
        self.prompt.setMinimumHeight(700)
        self.setLayout(mainVLayout)

    def showDocumentation(self):
        hiding = not self.docText.isHidden()

        if hiding:
            self.docBtn.setText("Show Documentation")
            self.docText.hide()
            self.textEdit.show()
            # self.prompt.setMinimumWidth(self.minWidth)
            self.prompt.resize(self.prompt.sizeHint())
        else:
            self.docBtn.setText("Show Code")
            self.textEdit.hide()
            self.docText.show()


            self.prompt.resize(self.prompt.sizeHint())

    def getCode(self):
        return self.textEdit.getText()

    def verifyCode(self):
        # Checks if the users code is valid, and updates self.applyBtn
        edit  = self.textEdit.getTextEdit()
        code  = self.textEdit.getText()

        # print("Running check")
        # print("\t" in code)
        # newCode = code[:]
        # newCode = newCode.replace("\t", "    ")
        #
        # if not newCode == code:
        #     edit.textChanged.disconnect()
        #     cursor    = edit.textCursor()
        #     print("position before: ", cursor.position())
        #     currPosition = cursor.position() + 3
        #     edit.replace(code, newCode)
        #
        #     cursor.setPosition(currPosition)
        #     print("position after: ", cursor.position())
        #
        #     edit.textChanged.connect(self.verifyCode)
        #
        #     # cursor = QtGui.QCursor()
        #     edit.setTextCursor(cursor)



        error = ""

        try:
            ast.parse(code)
        except SyntaxError as e:
            error = str(e)

        self.prompt.applyBtn.setDisabled(len(error))
        self.hintLbl.setText(error)


# Center a window on the current screen
def centerScreen(self):
        frameGm = self.frameGeometry()
        screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        print("Centerpoint: ", centerPoint, screen)
        self.move(frameGm.topLeft())