# -*- coding: utf-8 -*-
# Kurum Rehberi
# Telif Hakkı (C) 2026 Mehmet Aykurt


import ctypes
import json
import os
import re
from datetime import datetime

import wx

import gui
import globalPluginHandler
import globalVars
import ui
from logHandler import log

from scriptHandler import script


DATA_FOLDER_NAME = "kurum_rehberi"
DATA_FILE_NAME = "rehber.json"
SETTINGS_FILE_NAME = "ayarlar.json"
HELP_FILE_NAME = "readme.html"


FIELD_DEFINITIONS = [
    {"key": "firstName", "label": "Ad", "detailName": "Seçili kaydın adı", "column": "Ad", "width": 120, "multiline": False},
    {"key": "lastName", "label": "Soyad", "detailName": "Seçili kaydın soyadı", "column": "Soyad", "width": 120, "multiline": False},
    {"key": "title", "label": "Görev/Unvan", "detailName": "Seçili kaydın görev veya unvan bilgisi", "column": "Görev/Unvan", "width": 150, "multiline": False},
    {"key": "unit", "label": "Birim", "detailName": "Seçili kaydın birim bilgisi", "column": "Birim", "width": 130, "multiline": False},
    {"key": "phone", "label": "Telefon Numarası", "detailName": "Seçili kaydın telefon numarası", "column": "Telefon Numarası", "width": 140, "multiline": False},
    {"key": "extension", "label": "Dahili Numara", "detailName": "Seçili kaydın dahili numarası", "column": "Dahili Numara", "width": 110, "multiline": False},
    {"key": "email", "label": "E-posta", "detailName": "Seçili kaydın e-posta adresi", "column": "E-posta", "width": 190, "multiline": False},
    {"key": "note", "label": "Not", "detailName": "Seçili kaydın not bilgisi", "column": "Not", "width": 220, "multiline": True},
]

FIELD_KEYS = [field["key"] for field in FIELD_DEFINITIONS]
DEFAULT_FIELD_VISIBILITY = dict((field["key"], True) for field in FIELD_DEFINITIONS)


def getDataFolderPath():
    basePath = globalVars.appArgs.configPath
    return os.path.join(basePath, DATA_FOLDER_NAME)


def getDataFilePath():
    return os.path.join(getDataFolderPath(), DATA_FILE_NAME)


def getSettingsFilePath():
    return os.path.join(getDataFolderPath(), SETTINGS_FILE_NAME)


def logWarning(message, exc_info=False):
    try:
        log.debugWarning("Kurum Rehberi: {0}".format(message), exc_info=exc_info)
    except Exception:
        pass


def getAddonRootPath():
    return os.path.dirname(os.path.dirname(__file__))


def getUniqueLanguageCodes():
    languageCodes = []

    try:
        import languageHandler
        currentLanguage = languageHandler.getLanguage()
    except Exception:
        currentLanguage = ""
        logWarning("NVDA dili alınamadı.", exc_info=True)

    if currentLanguage:
        normalizedLanguage = currentLanguage.replace("-", "_")
        languageCodes.append(normalizedLanguage)

        if "_" in normalizedLanguage:
            languageCodes.append(normalizedLanguage.split("_", 1)[0])

    languageCodes.extend(["tr", "en"])

    uniqueLanguageCodes = []
    for languageCode in languageCodes:
        if languageCode and languageCode not in uniqueLanguageCodes:
            uniqueLanguageCodes.append(languageCode)

    return uniqueLanguageCodes


def getHelpFileCandidates():
    addonRootPath = getAddonRootPath()
    candidates = []

    for languageCode in getUniqueLanguageCodes():
        candidates.append(os.path.join(addonRootPath, "doc", languageCode, HELP_FILE_NAME))

    candidates.append(os.path.join(addonRootPath, "doc", HELP_FILE_NAME))

    return candidates


def getExistingHelpFilePath():
    for candidatePath in getHelpFileCandidates():
        if os.path.exists(candidatePath):
            return candidatePath

    return None


def getExpectedHelpFilePath():
    candidates = getHelpFileCandidates()
    if candidates:
        return candidates[0]
    return os.path.join(getAddonRootPath(), "doc", "tr", HELP_FILE_NAME)


def getDocumentsFolderPath():
    try:
        from ctypes import wintypes

        class GUID(ctypes.Structure):
            _fields_ = [
                ("Data1", wintypes.DWORD),
                ("Data2", wintypes.WORD),
                ("Data3", wintypes.WORD),
                ("Data4", wintypes.BYTE * 8),
            ]

        folderIdDocuments = GUID(
            0xFDD39AD0,
            0x238F,
            0x46AF,
            (wintypes.BYTE * 8)(0xAD, 0xB4, 0x6C, 0x85, 0x48, 0x03, 0x69, 0xC7)
        )

        pathPointer = wintypes.LPWSTR()

        result = ctypes.windll.shell32.SHGetKnownFolderPath(
            ctypes.byref(folderIdDocuments),
            0,
            None,
            ctypes.byref(pathPointer)
        )

        if result == 0 and pathPointer.value:
            path = pathPointer.value
            ctypes.windll.ole32.CoTaskMemFree(pathPointer)
            return path

    except Exception:
        logWarning("Belgeler klasörü Windows bilinen klasör API'siyle alınamadı.", exc_info=True)

    return os.path.join(os.path.expanduser("~"), "Documents")


def normalizeTextValue(value):
    if value is None:
        return ""

    return str(value)


def normalizeRecord(record):
    if not isinstance(record, dict):
        record = {}

    return {
        "firstName": normalizeTextValue(record.get("firstName", "")),
        "lastName": normalizeTextValue(record.get("lastName", "")),
        "title": normalizeTextValue(record.get("title", "")),
        "unit": normalizeTextValue(record.get("unit", "")),
        "phone": normalizeTextValue(record.get("phone", "")),
        "extension": normalizeTextValue(record.get("extension", "")),
        "email": normalizeTextValue(record.get("email", "")),
        "note": normalizeTextValue(record.get("note", ""))
    }


def normalizeRecordList(data):
    if not isinstance(data, list):
        raise ValueError("Seçilen dosya geçerli bir rehber yedeği değildir.")

    records = []

    for record in data:
        records.append(normalizeRecord(record))

    return records


def normalizeFieldVisibility(data):
    visibility = dict(DEFAULT_FIELD_VISIBILITY)

    if isinstance(data, dict):
        rawVisibility = data.get("fieldVisibility", data)

        if isinstance(rawVisibility, dict):
            for key in FIELD_KEYS:
                if key in rawVisibility:
                    visibility[key] = bool(rawVisibility[key])

    if not any(visibility.values()):
        visibility = dict(DEFAULT_FIELD_VISIBILITY)

    return visibility


def loadFieldVisibilitySettings():
    settingsPath = getSettingsFilePath()

    if not os.path.exists(settingsPath):
        return dict(DEFAULT_FIELD_VISIBILITY)

    try:
        with open(settingsPath, "r", encoding="utf-8") as file:
            loadedData = json.load(file)

        return normalizeFieldVisibility(loadedData)

    except Exception:
        logWarning("Alan görünürlüğü ayarları okunamadı. Varsayılan ayarlar kullanılacak.", exc_info=True)
        return dict(DEFAULT_FIELD_VISIBILITY)


def saveFieldVisibilitySettings(fieldVisibility):
    dataFolderPath = getDataFolderPath()
    settingsPath = getSettingsFilePath()
    tempSettingsPath = settingsPath + ".tmp"

    normalizedVisibility = normalizeFieldVisibility(fieldVisibility)

    try:
        if not os.path.isdir(dataFolderPath):
            os.makedirs(dataFolderPath)

        with open(tempSettingsPath, "w", encoding="utf-8") as file:
            json.dump(
                {"fieldVisibility": normalizedVisibility},
                file,
                ensure_ascii=False,
                indent=2
            )

        os.replace(tempSettingsPath, settingsPath)
        return True

    except Exception:
        logWarning("Alan görünürlüğü ayarları kaydedilemedi.", exc_info=True)
        try:
            if os.path.exists(tempSettingsPath):
                os.remove(tempSettingsPath)
        except Exception:
            logWarning("Geçici ayar dosyası temizlenemedi.", exc_info=True)

        return False


def getVisibleFieldDefinitions(fieldVisibility):
    normalizedVisibility = normalizeFieldVisibility(fieldVisibility)

    visibleFields = [
        field for field in FIELD_DEFINITIONS
        if normalizedVisibility.get(field["key"], True)
    ]

    if not visibleFields:
        visibleFields = list(FIELD_DEFINITIONS)

    return visibleFields


def getRecordDisplayName(recordData):
    recordData = normalizeRecord(recordData)

    fullName = "{0} {1}".format(
        recordData["firstName"],
        recordData["lastName"]
    ).strip()

    if fullName:
        return fullName

    if recordData["phone"]:
        return recordData["phone"]

    if recordData["extension"]:
        return "Dahili {0}".format(recordData["extension"])

    if recordData["email"]:
        return recordData["email"]

    return "Seçili kayıt"


def getRecordSortKey(recordData):
    recordData = normalizeRecord(recordData)

    return (
        recordData["firstName"].casefold(),
        recordData["lastName"].casefold(),
        recordData["unit"].casefold(),
        recordData["title"].casefold(),
        recordData["phone"],
        recordData["extension"],
        recordData["email"].casefold(),
    )


def isDigitsOnly(value):
    if not value:
        return True

    return value.isdigit()


def isValidEmail(value):
    if not value:
        return True

    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.match(pattern, value) is not None


def recordMatchesSearch(recordData, searchText, visibleFieldKeys=None):
    searchText = searchText.strip().casefold()

    if not searchText:
        return True

    recordData = normalizeRecord(recordData)

    if visibleFieldKeys is None:
        visibleFieldKeys = FIELD_KEYS

    searchableValues = []

    for key in visibleFieldKeys:
        if key in recordData:
            searchableValues.append(recordData[key])

    searchableText = " ".join(searchableValues).casefold()

    return searchText in searchableText


def makeDisplayTextCtrl(parent, name, multiline=False):
    style = wx.TE_READONLY

    if multiline:
        style |= wx.TE_MULTILINE

    control = wx.TextCtrl(parent, style=style)
    control.SetName(name)

    control.SetBackgroundColour(
        wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
    )

    return control


def bindDigitsOnlyTextCtrl(control, fieldName):
    control.Bind(
        wx.EVT_CHAR,
        lambda event: digitsOnlyCharHandler(event, fieldName)
    )


def digitsOnlyCharHandler(event, fieldName):
    keyCode = event.GetKeyCode()

    allowedKeys = (
        wx.WXK_BACK,
        wx.WXK_DELETE,
        wx.WXK_LEFT,
        wx.WXK_RIGHT,
        wx.WXK_UP,
        wx.WXK_DOWN,
        wx.WXK_HOME,
        wx.WXK_END,
        wx.WXK_TAB,
        wx.WXK_SHIFT,
        wx.WXK_CONTROL,
        wx.WXK_ALT,
    )

    if keyCode in allowedKeys:
        event.Skip()
        return

    if event.ControlDown() and keyCode in (
        ord("A"),
        ord("a"),
        ord("C"),
        ord("c"),
        ord("V"),
        ord("v"),
        ord("X"),
        ord("x"),
    ):
        event.Skip()
        return

    if 48 <= keyCode <= 57:
        event.Skip()
        return

    if 324 <= keyCode <= 333:
        event.Skip()
        return

    ui.message("{0} alanına yalnızca rakam yazılabilir.".format(fieldName))


def cleanListValue(value):
    return str(value).replace("\r", " ").replace("\n", " ").replace("\t", " ").strip()


class RecordDialog(wx.Dialog):

    def __init__(self, parent, title="Yeni Kayıt", recordData=None, fieldVisibility=None):
        super(RecordDialog, self).__init__(parent, title=title, size=(580, 520))

        self.recordData = None
        self.initialRecordData = normalizeRecord(recordData)
        self.fieldVisibility = normalizeFieldVisibility(fieldVisibility)
        self.visibleFields = getVisibleFieldDefinitions(self.fieldVisibility)
        self.controlsByField = {}

        self._buildInterface()
        self._loadInitialRecord()
        self.CentreOnScreen()

        firstControl = self.getFirstVisibleControl()
        if firstControl is not None:
            firstControl.SetFocus()

    def getFirstVisibleControl(self):
        if not self.visibleFields:
            return None
        return self.controlsByField.get(self.visibleFields[0]["key"])

    def _buildInterface(self):
        panel = wx.Panel(self)
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        formSizer = wx.FlexGridSizer(rows=len(self.visibleFields), cols=2, vgap=8, hgap=8)
        formSizer.AddGrowableCol(1, 1)

        for field in self.visibleFields:
            fieldKey = field["key"]
            fieldLabel = wx.StaticText(panel, label="{0}:".format(field["label"]))

            if field.get("multiline", False):
                control = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
            else:
                control = wx.TextCtrl(panel)

            control.SetName(field["label"])

            if fieldKey == "phone":
                bindDigitsOnlyTextCtrl(control, "Telefon numarası")
            if fieldKey == "extension":
                bindDigitsOnlyTextCtrl(control, "Dahili numara")

            self.controlsByField[fieldKey] = control

            labelFlag = wx.ALIGN_TOP if field.get("multiline", False) else wx.ALIGN_CENTER_VERTICAL
            formSizer.Add(fieldLabel, 0, labelFlag)
            formSizer.Add(control, 1, wx.EXPAND)

        mainSizer.Add(formSizer, 1, wx.EXPAND | wx.ALL, 12)

        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.saveButton = wx.Button(panel, wx.ID_OK, label="&Kaydet")
        self.cancelButton = wx.Button(panel, wx.ID_CANCEL, label="İ&ptal")

        buttonSizer.AddStretchSpacer(1)
        buttonSizer.Add(self.saveButton, 0, wx.RIGHT, 8)
        buttonSizer.Add(self.cancelButton, 0)

        mainSizer.Add(buttonSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        panel.SetSizer(mainSizer)

        self.saveButton.SetDefault()
        self.SetEscapeId(wx.ID_CANCEL)
        self.saveButton.Bind(wx.EVT_BUTTON, self.onSave)
        self.cancelButton.Bind(wx.EVT_BUTTON, self.onCancel)

    def _loadInitialRecord(self):
        for field in self.visibleFields:
            fieldKey = field["key"]
            control = self.controlsByField.get(fieldKey)
            if control is not None:
                control.SetValue(self.initialRecordData[fieldKey])

    def getVisibleFieldValues(self):
        values = {}
        for field in self.visibleFields:
            fieldKey = field["key"]
            control = self.controlsByField.get(fieldKey)
            if control is not None:
                values[fieldKey] = control.GetValue().strip()
        return values

    def focusField(self, fieldKey):
        control = self.controlsByField.get(fieldKey)
        if control is not None:
            control.SetFocus()
            return True
        return False

    def onSave(self, event):
        visibleValues = self.getVisibleFieldValues()

        if not any(value for value in visibleValues.values()):
            wx.MessageBox(
                "Görünür alanlardan en az biri doldurulmalıdır.",
                "Eksik Bilgi",
                wx.OK | wx.ICON_WARNING,
                self
            )
            firstControl = self.getFirstVisibleControl()
            if firstControl is not None:
                firstControl.SetFocus()
            return

        phone = visibleValues.get("phone", "")
        extension = visibleValues.get("extension", "")
        email = visibleValues.get("email", "")

        if not isDigitsOnly(phone):
            wx.MessageBox(
                "Telefon numarası alanına yalnızca rakam yazılmalıdır.\n\nBoşluk, harf, tire, parantez veya başka işaret kullanmayın.",
                "Geçersiz Telefon Numarası",
                wx.OK | wx.ICON_WARNING,
                self
            )
            self.focusField("phone")
            return

        if not isDigitsOnly(extension):
            wx.MessageBox(
                "Dahili numara alanına yalnızca rakam yazılmalıdır.\n\nBoşluk, harf, tire, parantez veya başka işaret kullanmayın.",
                "Geçersiz Dahili Numara",
                wx.OK | wx.ICON_WARNING,
                self
            )
            self.focusField("extension")
            return

        if not isValidEmail(email):
            wx.MessageBox(
                "E-posta alanına geçerli bir e-posta adresi yazılmalıdır.\n\nÖrnek: adsoyad@kurum.gov.tr",
                "Geçersiz E-posta",
                wx.OK | wx.ICON_WARNING,
                self
            )
            self.focusField("email")
            return

        recordData = normalizeRecord(self.initialRecordData)
        for fieldKey, value in visibleValues.items():
            recordData[fieldKey] = value

        self.recordData = recordData
        self.EndModal(wx.ID_OK)

    def onCancel(self, event):
        self.recordData = None
        self.EndModal(wx.ID_CANCEL)

    def getRecordData(self):
        return self.recordData


class ImportExportDialog(wx.Dialog):

    def __init__(self, parent):
        super(ImportExportDialog, self).__init__(parent, title="İçe/Dışa Aktar", size=(430, 180))
        self._buildInterface()
        self.CentreOnScreen()
        self.exportButton.SetFocus()

    def _buildInterface(self):
        panel = wx.Panel(self)
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        infoText = wx.StaticText(panel, label="Kurum Rehberi kayıtlarını içe veya dışa aktarma işlemleri.")
        mainSizer.Add(infoText, 0, wx.ALL, 12)

        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.exportButton = wx.Button(panel, label="&Dışa Aktar")
        self.importButton = wx.Button(panel, label="&İçe Aktar")
        self.cancelButton = wx.Button(panel, wx.ID_CANCEL, label="İ&ptal")

        buttonSizer.AddStretchSpacer(1)
        buttonSizer.Add(self.exportButton, 0, wx.RIGHT, 8)
        buttonSizer.Add(self.importButton, 0, wx.RIGHT, 8)
        buttonSizer.Add(self.cancelButton, 0)
        mainSizer.Add(buttonSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)

        panel.SetSizer(mainSizer)
        self.SetEscapeId(wx.ID_CANCEL)
        self.exportButton.Bind(wx.EVT_BUTTON, self.onExport)
        self.importButton.Bind(wx.EVT_BUTTON, self.onImport)
        self.cancelButton.Bind(wx.EVT_BUTTON, self.onCancel)

    def onExport(self, event):
        parent = self.GetParent()
        if parent.exportRecordsToDocuments():
            self.EndModal(wx.ID_OK)

    def onImport(self, event):
        parent = self.GetParent()
        if parent.importRecordsFromFile():
            self.EndModal(wx.ID_OK)

    def onCancel(self, event):
        self.EndModal(wx.ID_CANCEL)


class SettingsDialog(wx.Dialog):

    def __init__(self, parent):
        super(SettingsDialog, self).__init__(parent, title="Kurum Rehberi Ayarları", size=(520, 430))
        self.fieldVisibility = loadFieldVisibilitySettings()
        self.checkBoxesByField = {}
        self.saved = False
        self._buildInterface()
        self.CentreOnScreen()
        firstCheckBox = self.getFirstCheckBox()
        if firstCheckBox is not None:
            firstCheckBox.SetFocus()

    def getFirstCheckBox(self):
        if not FIELD_DEFINITIONS:
            return None
        return self.checkBoxesByField.get(FIELD_DEFINITIONS[0]["key"])

    def _buildInterface(self):
        panel = wx.Panel(self)
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        infoText = wx.StaticText(
            panel,
            label=(
                "Kurum Rehberi alan ayarları.\n\n"
                "İşaretli alanlar listede, yeni kayıt penceresinde, düzenleme penceresinde, "
                "seçili kayıt bilgilerinde ve arama işleminde görünür. "
                "İşareti kaldırılan alanların eski kayıt verileri silinmez; yalnızca arayüzden gizlenir."
            )
        )
        mainSizer.Add(infoText, 0, wx.EXPAND | wx.ALL, 12)

        fieldsBox = wx.StaticBox(panel, label="Görünecek alanlar")
        fieldsSizer = wx.StaticBoxSizer(fieldsBox, wx.VERTICAL)

        for field in FIELD_DEFINITIONS:
            fieldKey = field["key"]
            checkBox = wx.CheckBox(panel, label=field["label"])
            checkBox.SetValue(bool(self.fieldVisibility.get(fieldKey, True)))
            checkBox.SetName(field["label"])
            self.checkBoxesByField[fieldKey] = checkBox
            fieldsSizer.Add(checkBox, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 6)

        mainSizer.Add(fieldsSizer, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)

        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.saveButton = wx.Button(panel, wx.ID_OK, label="&Kaydet")
        self.defaultsButton = wx.Button(panel, label="&Varsayılanlar")
        self.cancelButton = wx.Button(panel, wx.ID_CANCEL, label="İ&ptal")

        buttonSizer.AddStretchSpacer(1)
        buttonSizer.Add(self.saveButton, 0, wx.RIGHT, 8)
        buttonSizer.Add(self.defaultsButton, 0, wx.RIGHT, 8)
        buttonSizer.Add(self.cancelButton, 0)
        mainSizer.Add(buttonSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)

        panel.SetSizer(mainSizer)
        self.SetEscapeId(wx.ID_CANCEL)
        self.saveButton.Bind(wx.EVT_BUTTON, self.onSave)
        self.defaultsButton.Bind(wx.EVT_BUTTON, self.onDefaults)
        self.cancelButton.Bind(wx.EVT_BUTTON, self.onCancel)
        self.Bind(wx.EVT_CLOSE, self.onCancel)

    def getSelectedFieldVisibility(self):
        visibility = {}
        for field in FIELD_DEFINITIONS:
            fieldKey = field["key"]
            checkBox = self.checkBoxesByField[fieldKey]
            visibility[fieldKey] = checkBox.GetValue()
        return visibility

    def onSave(self, event):
        visibility = self.getSelectedFieldVisibility()

        if not any(visibility.values()):
            wx.MessageBox(
                "En az bir alan görünür olmalıdır.",
                "Kurum Rehberi Ayarları",
                wx.OK | wx.ICON_WARNING,
                self
            )
            firstCheckBox = self.getFirstCheckBox()
            if firstCheckBox is not None:
                firstCheckBox.SetFocus()
            return

        if not saveFieldVisibilitySettings(visibility):
            wx.MessageBox("Ayarlar kaydedilemedi.", "Kurum Rehberi Ayarları", wx.OK | wx.ICON_ERROR, self)
            return

        self.saved = True
        ui.message("Ayarlar kaydedildi.")
        self.EndModal(wx.ID_OK)

    def onDefaults(self, event):
        for field in FIELD_DEFINITIONS:
            fieldKey = field["key"]
            self.checkBoxesByField[fieldKey].SetValue(True)
        ui.message("Tüm alanlar işaretlendi.")

    def onCancel(self, event):
        self.saved = False
        self.EndModal(wx.ID_CANCEL)


class KurumRehberiDialog(wx.Dialog):

    def __init__(self, parent):
        super(KurumRehberiDialog, self).__init__(parent, title="Kurum Rehberi", size=(1050, 760))

        self.fieldVisibility = loadFieldVisibilitySettings()
        self.visibleFields = getVisibleFieldDefinitions(self.fieldVisibility)
        self.visibleFieldKeys = [field["key"] for field in self.visibleFields]

        self.records = []
        self.displayedRecordIndexes = []
        self.detailTextControls = []
        self.detailControlsByField = {}
        self.pendingSearchMessage = ""

        self.searchAnnouncementTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onSearchAnnouncementTimer, self.searchAnnouncementTimer)

        self._buildInterface()
        self.loadRecords()
        self.CentreOnScreen()
        self.searchText.SetFocus()

    def _buildInterface(self):
        panel = wx.Panel(self)
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        titleText = wx.StaticText(panel, label="Kurum Rehberi")
        mainSizer.Add(titleText, 0, wx.ALL, 10)

        searchSizer = wx.BoxSizer(wx.HORIZONTAL)
        searchLabel = wx.StaticText(panel, label="Arama:")
        self.searchText = wx.TextCtrl(panel)
        self.searchText.SetName("Arama")
        self.clearSearchButton = wx.Button(panel, label="Aramayı Te&mizle")

        searchSizer.Add(searchLabel, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        searchSizer.Add(self.searchText, 1, wx.EXPAND | wx.RIGHT, 8)
        searchSizer.Add(self.clearSearchButton, 0)
        mainSizer.Add(searchSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        listTitleText = wx.StaticText(panel, label="Kayıt listesi")
        mainSizer.Add(listTitleText, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        self.recordList = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN)
        self.recordList.SetName("Kayıt listesi")

        for columnIndex, field in enumerate(self.visibleFields):
            self.recordList.InsertColumn(columnIndex, field["column"], width=field["width"])

        mainSizer.Add(self.recordList, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        detailTitleText = wx.StaticText(panel, label="Seçili kayıt bilgileri")
        mainSizer.Add(detailTitleText, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        detailSizer = wx.FlexGridSizer(rows=len(self.visibleFields), cols=2, vgap=6, hgap=8)
        detailSizer.AddGrowableCol(1, 1)

        for field in self.visibleFields:
            fieldKey = field["key"]
            selectedLabel = wx.StaticText(panel, label="{0}:".format(field["label"]))
            selectedText = makeDisplayTextCtrl(panel, field["detailName"], multiline=field.get("multiline", False))
            self.detailTextControls.append(selectedText)
            self.detailControlsByField[fieldKey] = selectedText
            labelFlag = wx.ALIGN_TOP if field.get("multiline", False) else wx.ALIGN_CENTER_VERTICAL
            detailSizer.Add(selectedLabel, 0, labelFlag)
            detailSizer.Add(selectedText, 1, wx.EXPAND)

        mainSizer.Add(detailSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.newButton = wx.Button(panel, label="&Yeni Kayıt")
        self.editButton = wx.Button(panel, label="Dü&zenle")
        self.deleteButton = wx.Button(panel, label="&Sil")
        self.importExportButton = wx.Button(panel, label="İçe/Dışa &Aktar")
        self.closeButton = wx.Button(panel, label="&Kapat")

        buttonSizer.Add(self.newButton, 0, wx.RIGHT, 8)
        buttonSizer.Add(self.editButton, 0, wx.RIGHT, 8)
        buttonSizer.Add(self.deleteButton, 0, wx.RIGHT, 8)
        buttonSizer.AddStretchSpacer(1)
        buttonSizer.Add(self.importExportButton, 0, wx.RIGHT, 8)
        buttonSizer.Add(self.closeButton, 0)
        mainSizer.Add(buttonSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        panel.SetSizer(mainSizer)

        self.searchText.Bind(wx.EVT_TEXT, self.onSearchTextChanged)
        self.clearSearchButton.Bind(wx.EVT_BUTTON, self.onClearSearch)
        self.recordList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onRecordSelected)
        self.recordList.Bind(wx.EVT_KEY_DOWN, self.onRecordListKeyDown)
        self.newButton.Bind(wx.EVT_BUTTON, self.onNewRecord)
        self.editButton.Bind(wx.EVT_BUTTON, self.onEditRecord)
        self.deleteButton.Bind(wx.EVT_BUTTON, self.onDeleteRecord)
        self.importExportButton.Bind(wx.EVT_BUTTON, self.onImportExport)
        self.closeButton.Bind(wx.EVT_BUTTON, self.onClose)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.EVT_CHAR_HOOK, self.onCharHook)
        self.setupTabOrder()

    def setupTabOrder(self):
        self.tabOrder = [self.searchText, self.clearSearchButton, self.recordList]
        self.tabOrder.extend(self.detailTextControls)
        self.tabOrder.extend([self.newButton, self.editButton, self.deleteButton, self.importExportButton, self.closeButton])

        for index in range(1, len(self.tabOrder)):
            self.tabOrder[index].MoveAfterInTabOrder(self.tabOrder[index - 1])

    def onRecordListKeyDown(self, event):
        keyCode = event.GetKeyCode()

        if keyCode in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            self.editSelectedRecord()
            return

        if keyCode == wx.WXK_DELETE:
            self.deleteSelectedRecord()
            return

        event.Skip()

    def onCharHook(self, event):
        keyCode = event.GetKeyCode()
        currentFocus = wx.Window.FindFocus()

        if event.AltDown() and keyCode in (ord("C"), ord("c")):
            if currentFocus in self.detailTextControls:
                self.copyFocusedDetailText(currentFocus)
                return
            event.Skip()
            return

        if event.AltDown() and keyCode in (ord("T"), ord("t")):
            self.copySelectedRecordField("phone", "Telefon numarası")
            return

        if event.AltDown() and keyCode in (ord("D"), ord("d")):
            self.copySelectedRecordField("extension", "Dahili numara")
            return

        if event.AltDown() and keyCode in (ord("E"), ord("e")):
            self.copySelectedRecordField("email", "E-posta")
            return

        if event.AltDown() and keyCode in (ord("S"), ord("s")):
            self.deleteSelectedRecord()
            return

        if keyCode == wx.WXK_DELETE:
            if currentFocus == self.recordList:
                self.deleteSelectedRecord()
                return
            event.Skip()
            return

        if keyCode in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            if currentFocus == self.searchText or currentFocus == self.recordList or currentFocus in self.detailTextControls:
                self.editSelectedRecord()
                return
            event.Skip()
            return

        if keyCode != wx.WXK_TAB:
            event.Skip()
            return

        if currentFocus not in self.tabOrder:
            event.Skip()
            return

        currentIndex = self.tabOrder.index(currentFocus)
        nextIndex = currentIndex - 1 if event.ShiftDown() else currentIndex + 1

        if nextIndex < 0:
            nextIndex = len(self.tabOrder) - 1
        if nextIndex >= len(self.tabOrder):
            nextIndex = 0

        self.tabOrder[nextIndex].SetFocus()

    def sortRecords(self):
        self.records.sort(key=getRecordSortKey)

    def findRecordIndex(self, recordData):
        for index, currentRecord in enumerate(self.records):
            if currentRecord is recordData:
                return index

        for index, currentRecord in enumerate(self.records):
            if currentRecord == recordData:
                return index

        return -1

    def onSearchTextChanged(self, event):
        count = self.applySearchFilter()
        self.queueSearchAnnouncement(count)
        event.Skip()

    def onSearchAnnouncementTimer(self, event):
        if self.pendingSearchMessage:
            message = self.pendingSearchMessage
            self.pendingSearchMessage = ""
            ui.message(message)

    def queueSearchAnnouncement(self, count):
        searchText = self.searchText.GetValue().strip()
        if searchText:
            self.pendingSearchMessage = "{0} kayıt bulundu.".format(count)
        else:
            self.pendingSearchMessage = "{0} kayıt listelendi.".format(count)
        self.searchAnnouncementTimer.StartOnce(350)

    def onClearSearch(self, event):
        self.clearSearchWithoutEvent()
        count = self.applySearchFilter()
        self.searchText.SetFocus()
        ui.message("Arama temizlendi. {0} kayıt listelendi.".format(count))

    def applySearchFilter(self, selectRecordIndex=None):
        searchText = self.searchText.GetValue()
        self.recordList.DeleteAllItems()
        self.displayedRecordIndexes = []

        for recordIndex, recordData in enumerate(self.records):
            if recordMatchesSearch(recordData, searchText, self.visibleFieldKeys):
                self.displayedRecordIndexes.append(recordIndex)
                self.insertRecordToList(recordData, selectRecord=False)

        count = self.recordList.GetItemCount()

        if count == 0:
            self.clearSelectedRecordDetails()
            return 0

        displayIndexToSelect = 0
        if selectRecordIndex is not None and selectRecordIndex in self.displayedRecordIndexes:
            displayIndexToSelect = self.displayedRecordIndexes.index(selectRecordIndex)

        self.recordList.Select(displayIndexToSelect)
        self.recordList.Focus(displayIndexToSelect)
        realRecordIndex = self.displayedRecordIndexes[displayIndexToSelect]
        self.showRecordDetails(realRecordIndex)
        return count

    def copyFocusedDetailText(self, control):
        text = control.GetValue()
        if not text:
            ui.message("Alan boş.")
            return
        if self.copyTextToClipboard(text):
            ui.message("{0} kopyalandı.".format(control.GetName()))
        else:
            ui.message("Panoya kopyalanamadı.")

    def copySelectedRecordField(self, fieldName, spokenFieldName):
        if not self.fieldVisibility.get(fieldName, True):
            ui.message("{0} alanı ayarlardan kapalı.".format(spokenFieldName))
            return

        selectedIndex = self.getSelectedRecordIndex()
        if selectedIndex == -1:
            ui.message("Kopyalamak için önce listeden bir kayıt seçmelisiniz.")
            return

        recordData = normalizeRecord(self.records[selectedIndex])
        text = recordData.get(fieldName, "")

        if not text:
            ui.message("{0} alanı boş.".format(spokenFieldName))
            return

        if self.copyTextToClipboard(text):
            ui.message("{0} kopyalandı.".format(spokenFieldName))
        else:
            ui.message("Panoya kopyalanamadı.")

    def copyTextToClipboard(self, text):
        if not wx.TheClipboard.Open():
            logWarning("Pano açılamadı.")
            return False

        try:
            data = wx.TextDataObject()
            data.SetText(text)
            wx.TheClipboard.SetData(data)
            wx.TheClipboard.Flush()
            return True
        except Exception:
            logWarning("Metin panoya kopyalanamadı.", exc_info=True)
            return False
        finally:
            wx.TheClipboard.Close()

    def getSelectedRecordIndex(self):
        displayIndex = self.recordList.GetFirstSelected()
        if displayIndex == -1:
            return -1
        if displayIndex < 0 or displayIndex >= len(self.displayedRecordIndexes):
            return -1
        recordIndex = self.displayedRecordIndexes[displayIndex]
        if recordIndex < 0 or recordIndex >= len(self.records):
            return -1
        return recordIndex

    def loadRecords(self):
        dataFilePath = getDataFilePath()
        if not os.path.exists(dataFilePath):
            self.clearSelectedRecordDetails()
            return

        try:
            with open(dataFilePath, "r", encoding="utf-8") as file:
                loadedData = json.load(file)
        except Exception as error:
            wx.MessageBox(
                "Rehber kayıt dosyası okunamadı.\n\nDosya yolu:\n{0}\n\nHata:\n{1}".format(dataFilePath, error),
                "Kurum Rehberi",
                wx.OK | wx.ICON_ERROR,
                self
            )
            self.clearSelectedRecordDetails()
            return

        try:
            self.records = normalizeRecordList(loadedData)
            self.sortRecords()
        except Exception as error:
            wx.MessageBox(
                "Rehber kayıt dosyası beklenen biçimde değil.\n\nDosya yolu:\n{0}\n\nHata:\n{1}".format(dataFilePath, error),
                "Kurum Rehberi",
                wx.OK | wx.ICON_ERROR,
                self
            )
            self.clearSelectedRecordDetails()
            return

        self.applySearchFilter()

    def saveRecords(self):
        dataFolderPath = getDataFolderPath()
        dataFilePath = getDataFilePath()
        tempFilePath = dataFilePath + ".tmp"

        try:
            if not os.path.isdir(dataFolderPath):
                os.makedirs(dataFolderPath)

            with open(tempFilePath, "w", encoding="utf-8") as file:
                json.dump(self.records, file, ensure_ascii=False, indent=2)

            os.replace(tempFilePath, dataFilePath)
            return True

        except Exception as error:
            try:
                if os.path.exists(tempFilePath):
                    os.remove(tempFilePath)
            except Exception:
                logWarning("Geçici rehber dosyası temizlenemedi.", exc_info=True)

            wx.MessageBox(
                "Kayıtlar rehber dosyasına yazılamadı.\n\nDosya yolu:\n{0}\n\nHata:\n{1}".format(dataFilePath, error),
                "Kurum Rehberi",
                wx.OK | wx.ICON_ERROR,
                self
            )
            return False

    def refreshRecordList(self):
        return self.applySearchFilter()

    def clearSearchWithoutEvent(self):
        self.searchText.ChangeValue("")

    def onNewRecord(self, event):
        dialog = RecordDialog(self, title="Yeni Kayıt", fieldVisibility=self.fieldVisibility)
        try:
            result = dialog.ShowModal()
            if result == wx.ID_OK:
                recordData = dialog.getRecordData()
                if recordData:
                    recordData = normalizeRecord(recordData)
                    self.records.append(recordData)
                    self.sortRecords()
                    newRecordIndex = self.findRecordIndex(recordData)
                    self.clearSearchWithoutEvent()
                    self.applySearchFilter(selectRecordIndex=newRecordIndex)
                    if self.saveRecords():
                        ui.message("Kayıt kaydedildi.")
        finally:
            dialog.Destroy()
        self.searchText.SetFocus()

    def onEditRecord(self, event):
        self.editSelectedRecord()

    def editSelectedRecord(self):
        selectedIndex = self.getSelectedRecordIndex()
        if selectedIndex == -1:
            wx.MessageBox("Düzenlemek için önce listeden bir kayıt seçmelisiniz.", "Kurum Rehberi", wx.OK | wx.ICON_WARNING, self)
            self.recordList.SetFocus()
            return

        dialog = RecordDialog(self, title="Kaydı Düzenle", recordData=self.records[selectedIndex], fieldVisibility=self.fieldVisibility)
        try:
            result = dialog.ShowModal()
            if result == wx.ID_OK:
                recordData = dialog.getRecordData()
                if recordData:
                    recordData = normalizeRecord(recordData)
                    self.records[selectedIndex] = recordData
                    self.sortRecords()
                    newRecordIndex = self.findRecordIndex(recordData)
                    self.applySearchFilter(selectRecordIndex=newRecordIndex)
                    if self.saveRecords():
                        ui.message("Kayıt güncellendi.")
        finally:
            dialog.Destroy()
        self.recordList.SetFocus()

    def onDeleteRecord(self, event):
        self.deleteSelectedRecord()

    def deleteSelectedRecord(self):
        selectedIndex = self.getSelectedRecordIndex()
        if selectedIndex == -1:
            wx.MessageBox("Silmek için önce listeden bir kayıt seçmelisiniz.", "Kurum Rehberi", wx.OK | wx.ICON_WARNING, self)
            self.recordList.SetFocus()
            return

        recordData = normalizeRecord(self.records[selectedIndex])
        displayName = getRecordDisplayName(recordData)
        answer = wx.MessageBox("{0} kaydı silinsin mi?\n\nBu işlem geri alınamaz.".format(displayName), "Silme Onayı", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING, self)
        if answer != wx.YES:
            self.recordList.SetFocus()
            return

        deletedRecord = self.records.pop(selectedIndex)
        if not self.saveRecords():
            self.records.insert(selectedIndex, deletedRecord)
            self.sortRecords()
            self.applySearchFilter()
            self.recordList.SetFocus()
            return

        self.applySearchFilter()
        self.recordList.SetFocus()
        wx.CallLater(150, ui.message, "Kayıt silinmiştir.")

    def insertRecordToList(self, recordData, selectRecord=True):
        index = self.recordList.GetItemCount()
        recordData = normalizeRecord(recordData)
        if not self.visibleFields:
            return

        firstField = self.visibleFields[0]
        self.recordList.InsertItem(index, cleanListValue(recordData[firstField["key"]]))

        for columnIndex, field in enumerate(self.visibleFields[1:], start=1):
            self.recordList.SetItem(index, columnIndex, cleanListValue(recordData[field["key"]]))

        if selectRecord:
            self.recordList.Select(index)
            self.recordList.Focus(index)
            self.recordList.SetFocus()

    def onRecordSelected(self, event):
        displayIndex = event.GetIndex()
        if displayIndex < 0 or displayIndex >= len(self.displayedRecordIndexes):
            self.clearSelectedRecordDetails()
            event.Skip()
            return
        recordIndex = self.displayedRecordIndexes[displayIndex]
        self.showRecordDetails(recordIndex)
        event.Skip()

    def showRecordDetails(self, recordIndex):
        if recordIndex < 0 or recordIndex >= len(self.records):
            self.clearSelectedRecordDetails()
            return
        recordData = normalizeRecord(self.records[recordIndex])
        for field in self.visibleFields:
            fieldKey = field["key"]
            control = self.detailControlsByField.get(fieldKey)
            if control is not None:
                control.SetValue(recordData[fieldKey])

    def clearSelectedRecordDetails(self):
        for control in self.detailTextControls:
            control.SetValue("")

    def ensureDocumentsFolderExists(self, operationTitle):
        documentsPath = getDocumentsFolderPath()
        if os.path.isdir(documentsPath):
            return documentsPath

        try:
            os.makedirs(documentsPath)
            return documentsPath
        except Exception as error:
            wx.MessageBox(
                "Belgeler klasörüne erişilemedi.\n\nYol:\n{0}\n\nHata:\n{1}".format(documentsPath, error),
                operationTitle,
                wx.OK | wx.ICON_ERROR,
                self
            )
            logWarning("Belgeler klasörüne erişilemedi.", exc_info=True)
            return None

    def writeRecordsToJsonFile(self, records, filePath):
        tempFilePath = filePath + ".tmp"

        try:
            with open(tempFilePath, "w", encoding="utf-8") as file:
                json.dump(records, file, ensure_ascii=False, indent=2)

            os.replace(tempFilePath, filePath)
            return True
        except Exception:
            logWarning("JSON dosyası yazılamadı: {0}".format(filePath), exc_info=True)
            try:
                if os.path.exists(tempFilePath):
                    os.remove(tempFilePath)
            except Exception:
                logWarning("Geçici JSON dosyası temizlenemedi: {0}".format(tempFilePath), exc_info=True)

            return False

    def createAutomaticBackupBeforeImport(self):
        if not self.records:
            return None

        documentsPath = self.ensureDocumentsFolderExists("İçe Aktar")
        if documentsPath is None:
            return False

        fileName = "kurum_rehberi_ice_aktarma_oncesi_yedek_{0}.json".format(
            datetime.now().strftime("%Y%m%d_%H%M%S")
        )
        backupPath = os.path.join(documentsPath, fileName)

        if not self.writeRecordsToJsonFile(self.records, backupPath):
            wx.MessageBox(
                "İçe aktarma başlamadan önce mevcut kayıtların otomatik yedeği alınamadı.\n\n"
                "Veri güvenliği için içe aktarma işlemi iptal edildi.",
                "İçe Aktar",
                wx.OK | wx.ICON_ERROR,
                self
            )
            return False

        return backupPath

    def exportRecordsToDocuments(self):
        documentsPath = self.ensureDocumentsFolderExists("Dışa Aktar")
        if documentsPath is None:
            return False

        fileName = "kurum_rehberi_yedek_{0}.json".format(datetime.now().strftime("%Y%m%d_%H%M%S"))
        exportPath = os.path.join(documentsPath, fileName)

        if not self.writeRecordsToJsonFile(self.records, exportPath):
            wx.MessageBox(
                "Yedek dosyası oluşturulamadı.\n\nYol:\n{0}".format(exportPath),
                "Dışa Aktar",
                wx.OK | wx.ICON_ERROR,
                self
            )
            return False

        wx.MessageBox(
            "Yedek dosya Belgeler klasörüne kaydedilmiştir.\n\nDosya adı:\n{0}".format(fileName),
            "Dışa Aktar",
            wx.OK | wx.ICON_INFORMATION,
            self
        )
        ui.message("Yedek dosya Belgeler klasörüne kaydedilmiştir.")
        return True

    def importRecordsFromFile(self):
        documentsPath = getDocumentsFolderPath()
        if not os.path.isdir(documentsPath):
            documentsPath = os.path.expanduser("~")

        with wx.FileDialog(self, message="İçe aktarılacak rehber yedeğini seçin", defaultDir=documentsPath, defaultFile="", wildcard="JSON dosyaları (*.json)|*.json|Tüm dosyalar (*.*)|*.*", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dialog:
            result = dialog.ShowModal()
            if result != wx.ID_OK:
                self.recordList.SetFocus()
                return False
            importPath = dialog.GetPath()

        answer = wx.MessageBox("Seçilen yedek dosyası içe aktarılacaktır.\n\nBu işlem mevcut rehber kayıtlarının yerine geçecektir.\n\nDevam etmek istiyor musunuz?", "İçe Aktarma Onayı", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING, self)
        if answer != wx.YES:
            self.recordList.SetFocus()
            return False

        try:
            with open(importPath, "r", encoding="utf-8") as file:
                loadedData = json.load(file)
            importedRecords = normalizeRecordList(loadedData)
            importedRecords.sort(key=getRecordSortKey)
        except Exception as error:
            wx.MessageBox("Seçilen dosya içe aktarılamadı.\n\nDosya:\n{0}\n\nHata:\n{1}".format(importPath, error), "İçe Aktar", wx.OK | wx.ICON_ERROR, self)
            self.recordList.SetFocus()
            return False

        backupPath = self.createAutomaticBackupBeforeImport()
        if backupPath is False:
            self.recordList.SetFocus()
            return False

        oldRecords = self.records
        self.records = importedRecords
        if not self.saveRecords():
            self.records = oldRecords
            self.refreshRecordList()
            self.recordList.SetFocus()
            return False

        self.clearSearchWithoutEvent()
        self.refreshRecordList()
        self.recordList.SetFocus()

        message = "Yedek dosya içe aktarılmıştır."
        if backupPath:
            message = (
                "{0}\n\n"
                "Mevcut kayıtların içe aktarma öncesi yedeği Belgeler klasörüne kaydedilmiştir.\n\n"
                "Yedek dosya adı:\n{1}"
            ).format(message, os.path.basename(backupPath))

        wx.MessageBox(message, "İçe Aktar", wx.OK | wx.ICON_INFORMATION, self)
        ui.message("Yedek dosya içe aktarılmıştır.")
        return True

    def onImportExport(self, event):
        dialog = ImportExportDialog(self)
        try:
            dialog.ShowModal()
        finally:
            dialog.Destroy()
        self.recordList.SetFocus()

    def onClose(self, event):
        self.EndModal(wx.ID_CLOSE)


class GlobalPlugin(globalPluginHandler.GlobalPlugin):

    def __init__(self):
        super(GlobalPlugin, self).__init__()

        self.dialog = None
        self.subMenu = None
        self.subMenuItem = None
        self.openMenuItem = None
        self.settingsMenuItem = None
        self.helpMenuItem = None

        self.createToolsMenu()

    def createToolsMenu(self):
        self.subMenu = wx.Menu()

        self.openMenuItem = self.subMenu.Append(
            wx.ID_ANY,
            "Kurum Rehberi'ni &Aç",
            "Kurum Rehberi penceresini açar"
        )

        self.settingsMenuItem = self.subMenu.Append(
            wx.ID_ANY,
            "A&yarlar",
            "Kurum Rehberi ayarlarını açar"
        )

        self.helpMenuItem = self.subMenu.Append(
            wx.ID_ANY,
            "&Yardım",
            "Kurum Rehberi yardım dosyasını açar"
        )

        try:
            self.subMenuItem = gui.mainFrame.sysTrayIcon.toolsMenu.AppendSubMenu(
                self.subMenu,
                "Kurum &Rehberi",
                "Kurum Rehberi işlemleri"
            )
        except AttributeError:
            self.subMenuItem = gui.mainFrame.sysTrayIcon.toolsMenu.Append(
                wx.ID_ANY,
                "Kurum &Rehberi",
                self.subMenu
            )

        gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onOpenFromMenu, self.openMenuItem)
        gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onSettingsFromMenu, self.settingsMenuItem)
        gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onHelpFromMenu, self.helpMenuItem)

    def terminate(self):
        self.closeOpenDialogForReload()

        for menuItem in (self.openMenuItem, self.settingsMenuItem, self.helpMenuItem):
            try:
                if menuItem is not None:
                    gui.mainFrame.sysTrayIcon.Unbind(wx.EVT_MENU, source=menuItem)
            except Exception:
                logWarning("Menü bağlantısı kaldırılamadı.", exc_info=True)

        try:
            if self.subMenuItem is not None:
                toolsMenu = gui.mainFrame.sysTrayIcon.toolsMenu

                try:
                    toolsMenu.Delete(self.subMenuItem)
                except Exception:
                    try:
                        itemId = self.subMenuItem.GetId()
                        toolsMenu.Delete(itemId)
                    except Exception:
                        try:
                            toolsMenu.Remove(self.subMenuItem)
                        except Exception:
                            logWarning("Kurum Rehberi menüsü kaldırılamadı.", exc_info=True)
        except Exception:
            logWarning("Kurum Rehberi menüsü temizlenemedi.", exc_info=True)

        self.openMenuItem = None
        self.settingsMenuItem = None
        self.helpMenuItem = None
        self.subMenuItem = None
        self.subMenu = None
        self.dialog = None

    def closeOpenDialogForReload(self):
        if self.dialog is None:
            return

        try:
            if self.dialog.IsShown():
                self.dialog.EndModal(wx.ID_CANCEL)
        except Exception:
            logWarning("Açık Kurum Rehberi penceresi kapatılamadı.", exc_info=True)
            try:
                self.dialog.Destroy()
            except Exception:
                logWarning("Açık Kurum Rehberi penceresi yok edilemedi.", exc_info=True)

    def onOpenFromMenu(self, event):
        wx.CallAfter(self.openKurumRehberi)

    def onSettingsFromMenu(self, event):
        wx.CallAfter(self.openSettingsDialog)

    def onHelpFromMenu(self, event):
        wx.CallAfter(self.showHelpMessage)

    @script(
        description="Kurum Rehberi penceresini açar",
        gesture="kb:NVDA+shift+r",
        category="Kurum Rehberi"
    )
    def script_openKurumRehberi(self, gesture):
        wx.CallAfter(self.openKurumRehberi)

    def openKurumRehberi(self):
        if self.dialog is not None and self.dialog.IsShown():
            self.dialog.Raise()
            self.dialog.SetFocus()
            ui.message("Kurum Rehberi zaten açık.")
            return

        gui.mainFrame.prePopup()
        dialog = None

        try:
            dialog = KurumRehberiDialog(gui.mainFrame)
            self.dialog = dialog
            dialog.ShowModal()
        except Exception:
            logWarning("Kurum Rehberi penceresi açılamadı veya beklenmeyen biçimde kapandı.", exc_info=True)
            wx.MessageBox(
                "Kurum Rehberi penceresi açılamadı. Ayrıntılar NVDA günlüğüne yazılmıştır.",
                "Kurum Rehberi",
                wx.OK | wx.ICON_ERROR,
                gui.mainFrame
            )
        finally:
            if dialog is not None:
                try:
                    dialog.Destroy()
                except Exception:
                    logWarning("Kurum Rehberi penceresi yok edilemedi.", exc_info=True)
            self.dialog = None
            gui.mainFrame.postPopup()

    def openSettingsDialog(self):
        gui.mainFrame.prePopup()
        dialog = None

        try:
            dialog = SettingsDialog(gui.mainFrame)
            result = dialog.ShowModal()

            if result == wx.ID_OK:
                if self.dialog is not None:
                    wx.MessageBox(
                        "Ayarlar kaydedildi.\n\n"
                        "Değişikliklerin uygulanması için Kurum Rehberi penceresini kapatıp yeniden açınız.",
                        "Kurum Rehberi Ayarları",
                        wx.OK | wx.ICON_INFORMATION,
                        gui.mainFrame
                    )
                else:
                    ui.message("Ayarlar kaydedildi.")
        except Exception:
            logWarning("Kurum Rehberi ayar penceresi açılamadı.", exc_info=True)
            wx.MessageBox(
                "Kurum Rehberi ayarları açılamadı. Ayrıntılar NVDA günlüğüne yazılmıştır.",
                "Kurum Rehberi Ayarları",
                wx.OK | wx.ICON_ERROR,
                gui.mainFrame
            )
        finally:
            if dialog is not None:
                try:
                    dialog.Destroy()
                except Exception:
                    logWarning("Kurum Rehberi ayar penceresi yok edilemedi.", exc_info=True)
            gui.mainFrame.postPopup()

    def showHelpMessage(self):
        helpFilePath = getExistingHelpFilePath()

        if helpFilePath is None:
            gui.mainFrame.prePopup()

            try:
                wx.MessageBox(
                    "Yardım dosyası bulunamadı.\n\n"
                    "Beklenen dosya yolu:\n{0}\n\n"
                    "Not: manifest.ini içinde docFileName değeri yalnızca readme.html olmalı; "
                    "Türkçe yardım dosyası doc/tr/readme.html konumunda bulunmalıdır.".format(
                        getExpectedHelpFilePath()
                    ),
                    "Kurum Rehberi Yardım",
                    wx.OK | wx.ICON_ERROR,
                    gui.mainFrame
                )
            finally:
                gui.mainFrame.postPopup()

            return

        try:
            os.startfile(helpFilePath)
            ui.message("Kurum Rehberi yardım dosyası açılıyor.")
        except Exception as error:
            gui.mainFrame.prePopup()

            try:
                wx.MessageBox(
                    "Yardım dosyası açılamadı.\n\n"
                    "Dosya yolu:\n{0}\n\n"
                    "Hata:\n{1}".format(helpFilePath, error),
                    "Kurum Rehberi Yardım",
                    wx.OK | wx.ICON_ERROR,
                    gui.mainFrame
                )
            finally:
                gui.mainFrame.postPopup()

            logWarning("Yardım dosyası açılamadı.", exc_info=True)
