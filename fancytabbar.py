#
#
#
# Copyright (c) 2016 liubin77 -- l.bin.2008 (at) gmail (dot) com
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import sys

from PyQt4.QtGui import *
from PyQt4.QtCore import *


class StyleHelper():
    # DEFAULT_BASE_COLOR = 0x666666
    m_baseColor = QColor(102, 102, 102)
    m_requestedBaseColor = QColor(0, 0, 0)

    @staticmethod
    def sidebarFontSize():
        if sys.platform == "darwin":
            return 10
        else:
            return 7.5

    @staticmethod
    def panelTextColor(lightColored=False):
        if not lightColored:
            return Qt.white
        else:
            return Qt.black

    @staticmethod
    def baseColor(lightColored=False):
        if not lightColored:
            return StyleHelper.m_baseColor
        else:
            return StyleHelper.m_baseColor.lighter(230)

    @staticmethod
    def borderColor(lightColored=False):
        result = StyleHelper.baseColor(lightColored)
        result.setHsv(result.hue(),
                      result.saturation(),
                      result.value() / 2)
        return result

    @staticmethod
    def setBaseColor(newcolor):
        StyleHelper.m_requestedBaseColor = newcolor

        color = QColor()
        color.setHsv(newcolor.hue(),
                     newcolor.saturation() * 0.7,
                     64 + newcolor.value() / 3)

        if color.isValid() and color != StyleHelper.m_baseColor:
            StyleHelper.m_baseColor = color
            for w in QApplication.topLevelWidgets():
                w.update()

    @staticmethod
    def drawIconWithShadow(icon, rect, p, iconMode, radius=3, color=QColor(0, 0, 0, 130), offset=QPoint(1, -2)):
        # cache = QPixmap()
        # pixmapName = "icon %s %s %s" % (icon.cacheKey(), iconMode, rect.height())
        #
        # if not QPixmapCache.find(pixmapName, cache):
        px = icon.pixmap(rect.size())
        # cache = QPixmap(px.size() + QSize(radius * 2, radius *2))
        # cache.fill(Qt.transparent)
        #
        # cachePainter = QPainter(cache)
        if iconMode == QIcon.Disabled:
            im = px.toImage().convertToFormat(QImage.Format_ARGB32)
            for y in range(im.height()):
                scanLine = im.scanLine(y)
                for x in range(im.width()):
                    pixel = scanLine
                    intensity = qGray(pixel)
                    scanLine = qRgba(intensity, intensity, intensity, qAlpha(pixel))
                    scanLine += 1
            px = QPixmap.fromImage(im)

        # Draw shadow
        tmp = QImage(px.size() + QSize(radius * 2, radius * 2 + 1), QImage.Format_ARGB32_Premultiplied)
        tmp.fill(Qt.transparent)

        tmpPainter = QPainter(tmp)
        tmpPainter.setCompositionMode(QPainter.CompositionMode_Source)
        tmpPainter.drawPixmap(QPoint(radius, radius), px)
        tmpPainter.end()

        # blur the alpha channel
        blurred = QImage(tmp.size(), QImage.Format_ARGB32_Premultiplied)
        blurred.fill(Qt.transparent)
        blurPainter = QPainter(blurred)
        # qt_blurImage(blurPainter, tmp, radius, False, True)
        blurPainter.end()

        tmp = blurred

        # blacken the image...
        tmpPainter.begin(tmp)
        tmpPainter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        tmpPainter.fillRect(tmp.rect(), color)
        tmpPainter.end()
        #
        # tmpPainter.begin(tmp)
        # tmpPainter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        #     tmpPainter.fillRect(tmp.rect(), color)
        #     tmpPainter.end()
        #
        #     # draw the blurred drop shadow...
        #     cachePainter.drawImage(QRect(0, 0, cache.rect().width(), cache.rect().height()), tmp)
        #
        #     # Draw the actual pixmap...
        #     cachePainter.drawPixmap(QPoint(radius, radius) + offset, px)
        #     QPixmapCache.insert(pixmapName, cache)

        # targetRect = cache.rect()
        # targetRect.moveCenter(rect.center())
        targetRect = QRect()
        targetRect.setSize(px.size() + QSize(radius * 2, radius * 2))
        targetRect.moveCenter(rect.center())
        p.drawPixmap(targetRect.topLeft() - offset, px)

    @staticmethod
    def sidebarHighlight():
        return QColor(255, 255, 255, 40)


class FancyTabBar(QWidget):
    currentChanged = pyqtSignal(int)

    m_rounding = 22
    m_textPadding = 4

    def __init__(self, parent):
        super().__init__(parent)

        self.mHoverIndex = -1
        self.mCurrentIndex = -1

        self.mTimerTriggerChangedSignal = QTimer()
        self.mAttachedTabs = []

        self.setMinimumWidth(max(2 * self.m_rounding, 66))
        self.setMaximumWidth(self.tabSizeHint(False).width())
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        self.setAttribute(Qt.WA_Hover, True)
        self.setFocusPolicy(Qt.NoFocus)
        self.setMouseTracking(True)

        self.mTimerTriggerChangedSignal.setSingleShot(True)

        self.mTimerTriggerChangedSignal.timeout.connect(self.emitCurrentIndex)

    def tabSizeHint(self, minimum):
        boldFont = QFont()
        boldFont.setPointSizeF(StyleHelper.sidebarFontSize())
        boldFont.setBold(True)
        fm = QFontMetrics(boldFont)
        spacing = 8
        width = 60 + spacing + 2
        maxLabelwidth = 0
        for tab in range(self.count()):
            w = fm.width(self.tabText(tab))
            if w > maxLabelwidth:
                maxLabelwidth = w

        iconHeight = 0 if minimum else 40

        return QSize(max(width, maxLabelwidth + 4), iconHeight + spacing + fm.height())

    def paintEvent(self, event):
        # Q_UNUSED(event)
        painter = QPainter(self)

        rectangle = self.rect().adjusted(0, 1, 0, 0)
        lg = QLinearGradient()

        lg.setStart(rectangle.topLeft())
        lg.setFinalStop(rectangle.topRight())
        lg.setColorAt(0.0, QColor(64, 64, 64, 255))
        lg.setColorAt(1.0, QColor(130, 130, 130, 255))
        painter.fillRect(rectangle, lg)

        painter.setPen(StyleHelper.borderColor())
        painter.drawLine(rectangle.topRight() + QPoint(1, 0), rectangle.bottomRight() + QPoint(1, 0))

        painter.setPen(StyleHelper.sidebarHighlight())
        painter.drawLine(rectangle.topRight(), rectangle.bottomRight())

        for i in range(self.count()):
            if i != self.currentIndex():
                self.paintTab(painter, i)

        if self.currentIndex() != -1:
            self.paintTab(painter, self.currentIndex())

    def mouseMoveEvent(self, e):
        newHover = -1
        for i in range(self.count()):
            area = self.tabRect(i)
            if area.contains(e.pos()):
                newHover = i
                break

        if newHover == self.mHoverIndex:
            return

        if self.validIndex(self.mHoverIndex):
            self.mAttachedTabs[self.mHoverIndex].fadeOut()

        self.mHoverIndex = newHover

        if self.validIndex(self.mHoverIndex):
            self.mAttachedTabs[self.mHoverIndex].fadeIn()
            self.mHoverRect = self.tabRect(self.mHoverIndex)

    def event(self, event):
        if event.type() == QEvent.ToolTip:
            if self.validIndex(self.mHoverIndex):
                tt = self.tabToolTip(self.mHoverIndex)
                if len(tt) > 0:
                    QToolTip.showText(event.globalPos(), tt, self)
                    return True

        return QWidget.event(self, event)

    def enterEvent(self, e):
        # Q_UNUSED(e)
        self.mHoverRect = QRect()
        self.mHoverIndex = -1

    def leaveEvent(self, *e):
        # Q_UNUSED(e)
        self.mHoverIndex = -1
        self.mHoverRect = QRect()
        for tab in self.mAttachedTabs:
            tab.fadeOut()

    def sizeHint(self):
        sh = self.tabSizeHint(False)
        return QSize(sh.width(), sh.height() * len(self.mAttachedTabs))

    def minimumSizeHint(self):
        sh = self.tabSizeHint(True)
        return QSize(sh.width(), sh.height() * len(self.mAttachedTabs))

    def tabRect(self, index):
        sh = self.tabSizeHint(False)

        if sh.height() * len(self.mAttachedTabs) > self.height():
            sh.setHeight(self.height() / len(self.mAttachedTabs))

        return QRect(0, index * sh.height(), sh.width(), sh.height())

    def emitCurrentIndex(self):
        self.currentChanged.emit(self.mCurrentIndex)

    def mousePressEvent(self, e):
        e.accept()
        for index in range(len(self.mAttachedTabs)):
            if self.tabRect(index).contains(e.pos()):
                if self.isTabEnabled(index):
                    self.mCurrentIndex = index
                    self.update()
                    self.mTimerTriggerChangedSignal.start(0)
                break

    def paintTab(self, painter, tabIndex):
        if not self.validIndex(tabIndex):
            qWarning("invalid index")
            return

        painter.save()

        rect = self.tabRect(tabIndex)
        selected = (tabIndex == self.mCurrentIndex)
        enabled = self.isTabEnabled(tabIndex)

        if selected:
            painter.save()
            grad = QLinearGradient(rect.topLeft(), rect.topRight())
            grad.setColorAt(0, QColor(255, 255, 255, 140))
            grad.setColorAt(1, QColor(255, 255, 255, 210))
            painter.fillRect(rect.adjusted(0, 1, 0, -1), grad)
            painter.restore()

            painter.setPen(QColor(0, 0, 0, 110))
            painter.drawLine(rect.topLeft() + QPoint(0, -1), rect.topRight() + QPoint(0, -1))
            painter.drawLine(rect.bottomLeft(), rect.bottomRight())

            painter.setPen(QColor(0, 0, 0, 40))
            painter.drawLine(rect.topLeft(), rect.bottomLeft())

            painter.setPen(QColor(255, 255, 255, 50))
            painter.drawLine(rect.topLeft() + QPoint(0, -2),
                             rect.topRight() + QPoint(0, -2))
            painter.drawLine(rect.bottomLeft() + QPoint(0, 1),
                             rect.bottomRight() + QPoint(0, 1))

            painter.setPen(QColor(255, 255, 255, 40))
            painter.drawLine(rect.topLeft(), rect.topRight())
            painter.drawLine(rect.topRight() + QPoint(0, 1), rect.bottomRight() + QPoint(0, -1))
            painter.drawLine(rect.bottomLeft() + QPoint(0, -1),
                             rect.bottomRight() + QPoint(0, -1))

        tabText = self.tabText(tabIndex)
        tabTextRect = QRect(rect)
        drawIcon = rect.height() > 36
        tabIconRect = QRect(tabTextRect)
        tabTextRect.translate(0, -2 if drawIcon else 1)
        boldFont = QFont(painter.font())
        boldFont.setPointSizeF(StyleHelper.sidebarFontSize())
        boldFont.setBold(True)
        painter.setFont(boldFont)
        painter.setPen(QColor(255, 255, 255, 160) if selected else QColor(0, 0, 0, 110))
        textFlags = Qt.AlignCenter | (Qt.AlignBottom if drawIcon else Qt.AlignVCenter) | Qt.TextWordWrap
        if enabled:
            painter.drawText(tabTextRect, textFlags, tabText)
            painter.setPen(QColor(60, 60, 60) if selected else StyleHelper.panelTextColor())
        else:
            painter.setPen(StyleHelper.panelTextColor() if selected else QColor(255, 255, 255, 120))

        if sys.platform == "darwin":
            isMac = True
        else:
            isMac = False

        if not isMac and not selected and enabled:
            painter.save()
            fader = int(self.mAttachedTabs[tabIndex].fader)
            grad = QLinearGradient(rect.topLeft(), rect.topRight())

            grad.setColorAt(0, Qt.transparent)
            grad.setColorAt(0.5, QColor(255, 255, 255, fader))
            grad.setColorAt(1, Qt.transparent)
            painter.fillRect(rect, grad)
            painter.setPen(QPen(grad, 1.0))

            painter.drawLine(rect.topLeft(), rect.topRight())
            painter.drawLine(rect.bottomLeft(), rect.bottomRight())

            painter.restore()

        if not enabled:
            painter.setOpacity(0.7)

        if drawIcon:
            textHeight = painter.fontMetrics().boundingRect(QRect(0, 0, self.width(), self.height()),
                                                            Qt.TextWordWrap, tabText).height()
            tabIconRect.adjust(0, 4, 0, -textHeight)
            StyleHelper.drawIconWithShadow(self.tabIcon(tabIndex), tabIconRect, painter,
                                           QIcon.Normal if enabled else QIcon.Disabled)

        painter.translate(0, -1)
        painter.drawText(tabTextRect, textFlags, tabText)
        painter.restore()


    def setCurrentIndex(self, index):
        if self.isTabEnabled(index):
            self.mCurrentIndex = index
            self.update()
            self.currentChanged.emit(self.mCurrentIndex)


    def setTabEnabled(self, index, enable):
        assert index < len(self.mAttachedTabs)
        assert index >= 0

        if len(self.mAttachedTabs) > index >= 0:
            self.mAttachedTabs[index].enabled = enable

        self.setMaximumWidth(self.tabSizeHint(False).width())
        self.update(self.tabRect(index))

    def isTabEnabled(self, index):
        assert index < len(self.mAttachedTabs)
        assert index >= 0

        if len(self.mAttachedTabs) > index >= 0:
            return self.mAttachedTabs[index].enabled

        return False

    def validIndex(self, index):
        return 0 <= index < len(self.mAttachedTabs)

    def setOrientation(self, p):
        self.mPosition = p

    def insertTab(self, index, icon, label):
        tab = FancyTab(self)
        tab.icon = icon
        tab.text = label
        self.mAttachedTabs.insert(index, tab)

    def removeTab(self, index):
        tab = self.mAttachedTabs[index]
        self.mAttachedTabs.remove(tab)

    def currentIndex(self):
        return self.mCurrentIndex

    def setTabToolTip(self, index, toolTip):
        self.mAttachedTabs[index].toolTip = toolTip

    def tabToolTip(self, index):
        return self.mAttachedTabs[index].toolTip

    def tabIcon(self, index):
        return self.mAttachedTabs[index].icon

    def tabText(self, index):
        return self.mAttachedTabs[index].text

    def count(self):
        return len(self.mAttachedTabs)


class FancyTab(QObject):
    def __init__(self, tabbar):
        super().__init__()
        self.enabled = True
        self.mTabBar = tabbar
        self.mFader = 0
        self.mAnimator = QPropertyAnimation()
        self.mAnimator.setTargetObject(self)
        self.mAnimator.setPropertyName("fader")
        self.icon = QIcon()
        self.text = ""
        self.toolTip = ""

    def fader(self):
        return self.mFader

    def setFader(self, fader):
        self.mFader = fader
        self.mTabBar.update()

    def fadeIn(self):
        self.mAnimator.stop()
        self.mAnimator.setDuration(200)
        self.mAnimator.setEndValue(60)
        self.mAnimator.start()

    def fadeOut(self):
        self.mAnimator.stop()
        self.mAnimator.setDuration(200)
        self.mAnimator.setEndValue(0)
        self.mAnimator.start()

    fader = pyqtProperty(float, fader, setFader)


class FancyTabWidget(QWidget):
    currentAboutToShow = pyqtSignal(int)
    currentChanged = pyqtSignal(int)

    def __init__(self, parent):
        super().__init__(parent)

        self._tabBar = FancyTabBar(self)
        self._selectionWidget = QWidget()
        selectionLayout = QVBoxLayout()
        selectionLayout.setSpacing(0)
        selectionLayout.setMargin(0)
        selectionLayout.addWidget(self._tabBar, 0)
        self._selectionWidget.setLayout(selectionLayout)
        self._selectionWidget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        self._modesStack = QStackedLayout()

        mainLayout = QHBoxLayout()
        mainLayout.setMargin(0)
        mainLayout.setSpacing(0)
        mainLayout.addWidget(self._selectionWidget)
        mainLayout.addLayout(self._modesStack)

        self.setLayout(mainLayout)

        self._tabBar.currentChanged.connect(self.showWidget)

    def setSelectionWidgetVisible(self, visible):
        self._selectionWidget.setVisible(visible)

    def isSelectionWidgetVisible(self):
        return self._selectionWidget.isVisible()

    selectionWidgetVisible = property(setSelectionWidgetVisible, isSelectionWidgetVisible)


    def insertTab(self, index, tab, icon, label):
        self._modesStack.insertWidget(index, tab)
        self._tabBar.insertTab(index, icon, label)

    def removeTab(self, index):
        self._modesStack.removeWidget(self._modesStack.widget(index))
        self._tabBar.removeTab(index)

    def setBackgroundBrush(self, brush):
        pal = self._tabBar.palette()
        pal.setBrush(QPalette.Mid, brush)
        self._tabBar.setPalette(pal)

    @property
    def currentIndex(self):
        return self._tabBar.currentIndex()

    @pyqtSlot()
    def setCurrentIndex(self, index: int):
        if self._tabBar.isTabEnabled(index):
            self._tabBar.setCurrentIndex(index)

    @pyqtSlot(int)
    def showWidget(self, index: int):
        self.currentAboutToShow.emit(index)
        self._modesStack.setCurrentIndex(index)
        self.currentChanged.emit(index)

    def setTabToolTip(self, index: int, toolTip: str):
        self._tabBar.setTabToolTip(index, toolTip)

    def setTabEnabled(self, index: int, enable: bool):
        self._tabBar.setTabEnabled(index, enable)

    @property
    def isTabEnabled(self, index) -> bool:
        return self._tabBar.isTabEnabled(index)