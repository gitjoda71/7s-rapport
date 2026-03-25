Attribute VB_Name = "MBlankett"
Option Explicit

' ============================================================================
' M-BLANKETT - Komplett VBA-makro (en enda modul)
'
' Anvandning:
'   1. Oppna Word > Alt+F11 > Infoga > Modul
'   2. Klistra in HELA denna kod i modulen
'   3. Stang VBA-editorn
'   4. Klistra in ratext i dokumentet
'   5. Kor makrot "SkapaMBlankett" (Alt+F8)
'
' Sparas i: hv/verktyg/m_blankett/src/vba/
' ============================================================================

' --- Datastruktur for parsade falt ---
Private Type MBlankettData
    Till        As String
    Fran        As String
    Tid         As String
    Amne        As String
    Sign        As String
    Bodytext    As String
End Type

' --- Layout-konstanter ---
Private Const TAB_COL2_CM As Single = 7       ' Mittkolumn (FRAN)
Private Const TAB_COL3_CM As Single = 13      ' Hogerkolumn (TID)
Private Const LABEL_FONT_SIZE As Single = 8
Private Const VALUE_FONT_SIZE As Single = 11
Private Const BODY_FONT_SIZE As Single = 11
Private Const BODY_LEFT_INDENT_CM As Single = 0.5
Private Const LABEL_FONT_COLOR As Long = 5263440  ' RGB(80,80,80)


' ############################################################################
'  HUVUDMAKRO
' ############################################################################

Public Sub SkapaMBlankett()
    On Error GoTo ErrorHandler

    Dim doc As Document
    Set doc = ActiveDocument

    ' --- Hamta ratext ---
    Dim sRawText As String
    sRawText = doc.Content.Text

    If Len(Trim$(sRawText)) = 0 Then
        MsgBox "Dokumentet ar tomt. Klistra in din ratext och kor makrot igen.", _
               vbInformation, "M-blankett"
        GoTo CleanUp
    End If

    ' --- Rensa dokumentet ---
    doc.Content.Text = ""

    ' --- Sidlayout ---
    With doc.PageSetup
        .Orientation = wdOrientPortrait
        .TopMargin = CentimetersToPoints(2)
        .BottomMargin = CentimetersToPoints(2)
        .LeftMargin = CentimetersToPoints(2.5)
        .RightMargin = CentimetersToPoints(2.5)
    End With

    ' --- Parsa ---
    Dim data As MBlankettData
    data = ParseText(sRawText)

    ' --- Bygg header ---
    Dim rng As Range
    Set rng = doc.Range(0, 0)
    Set rng = BuildHeader(rng, data)

    ' --- Bygg body ---
    Set rng = BuildBody(rng, data)

    ' Markoren till borjan
    doc.Range(0, 0).Select

CleanUp:
    Set rng = Nothing
    Set doc = Nothing
    Exit Sub

ErrorHandler:
    MsgBox "Ett ovantat fel uppstod: " & Err.Description & vbCrLf & _
           "(Felkod: " & Err.Number & ")", _
           vbExclamation, "M-blankett - Fel"
    Resume CleanUp
End Sub


' ############################################################################
'  PARSER
' ############################################################################

Private Function ParseText(ByVal sRawText As String) As MBlankettData
    Dim result As MBlankettData
    Dim sHeader As String
    Dim sBody As String
    Dim posDelimiter As Long

    ' Normalisera radbrytningar till vbLf
    sRawText = Replace(sRawText, vbCrLf, vbLf)
    sRawText = Replace(sRawText, vbCr, vbLf)

    ' --- Separera header fran body via "---" ---
    posDelimiter = InStr(1, sRawText, vbLf & "---", vbTextCompare)
    If posDelimiter = 0 Then
        posDelimiter = InStr(1, sRawText, "---" & vbLf, vbTextCompare)
    End If

    If posDelimiter > 0 Then
        sHeader = Left$(sRawText, posDelimiter - 1)
        Dim afterDelim As Long
        afterDelim = InStr(posDelimiter, sRawText, "---")
        sBody = Mid$(sRawText, afterDelim + 3)
        Do While Left$(sBody, 1) = vbLf
            sBody = Mid$(sBody, 2)
        Loop
    Else
        ' Fallback: dubbel radbrytning
        Dim posDouble As Long
        posDouble = InStr(1, sRawText, vbLf & vbLf)
        If posDouble > 0 And HasHeaderFields(Left$(sRawText, posDouble)) Then
            sHeader = Left$(sRawText, posDouble - 1)
            sBody = Mid$(sRawText, posDouble + 2)
        Else
            ' Ingen struktur - allt blir body
            sHeader = ""
            sBody = sRawText
        End If
    End If

    ' --- Extrahera falt ---
    result.Till = ExtractField(sHeader, "TILL")
    result.Fran = ExtractField(sHeader, "FR" & ChrW$(197) & "N")
    If Len(result.Fran) = 0 Then
        result.Fran = ExtractField(sHeader, "FRAN")
    End If
    result.Tid = ExtractField(sHeader, "TID")
    result.Amne = ExtractField(sHeader, "(" & ChrW$(196) & "MNE|AMNE|RUBRIK)")
    result.Sign = ExtractField(sHeader, "(SIGN|AVS SIGN|UNDERSKRIFT)")

    ' --- SIGN i slutet av body? ---
    If Len(result.Sign) = 0 Then
        result.Sign = ExtractFieldFromEnd(sBody, "(SIGN|AVS SIGN|UNDERSKRIFT)")
        If Len(result.Sign) > 0 Then
            sBody = RemoveFieldFromEnd(sBody, "(SIGN|AVS SIGN|UNDERSKRIFT)")
        End If
    End If

    result.Bodytext = Trim$(sBody)
    ParseText = result
End Function

Private Function ExtractField(ByVal sText As String, ByVal sFieldPattern As String) As String
    Dim oRegex As Object
    Dim oMatches As Object
    Set oRegex = CreateObject("VBScript.RegExp")
    oRegex.IgnoreCase = True
    oRegex.MultiLine = True
    oRegex.Pattern = "^" & sFieldPattern & ":\s*(.*?)$"
    Set oMatches = oRegex.Execute(sText)
    If oMatches.Count > 0 Then
        ExtractField = Trim$(oMatches(0).SubMatches(0))
    Else
        ExtractField = ""
    End If
    Set oMatches = Nothing
    Set oRegex = Nothing
End Function

Private Function ExtractFieldFromEnd(ByVal sText As String, ByVal sFieldPattern As String) As String
    Dim oRegex As Object
    Dim oMatches As Object
    Set oRegex = CreateObject("VBScript.RegExp")
    oRegex.IgnoreCase = True
    oRegex.MultiLine = True
    oRegex.Pattern = sFieldPattern & ":\s*(.*?)$"
    Set oMatches = oRegex.Execute(sText)
    If oMatches.Count > 0 Then
        ExtractFieldFromEnd = Trim$(oMatches(oMatches.Count - 1).SubMatches(0))
    Else
        ExtractFieldFromEnd = ""
    End If
    Set oMatches = Nothing
    Set oRegex = Nothing
End Function

Private Function RemoveFieldFromEnd(ByVal sText As String, ByVal sFieldPattern As String) As String
    Dim oRegex As Object
    Set oRegex = CreateObject("VBScript.RegExp")
    oRegex.IgnoreCase = True
    oRegex.MultiLine = True
    oRegex.Global = True
    oRegex.Pattern = "\n?" & sFieldPattern & ":\s*.*?$"
    RemoveFieldFromEnd = oRegex.Replace(sText, "")
    Set oRegex = Nothing
End Function

Private Function HasHeaderFields(ByVal sText As String) As Boolean
    Dim oRegex As Object
    Set oRegex = CreateObject("VBScript.RegExp")
    oRegex.IgnoreCase = True
    oRegex.MultiLine = True
    oRegex.Pattern = "^(TILL|FR" & ChrW$(197) & "N|FRAN|TID|" & ChrW$(196) & "MNE|AMNE|RUBRIK|SIGN|AVS SIGN):"
    HasHeaderFields = oRegex.Test(sText)
    Set oRegex = Nothing
End Function


' ############################################################################
'  HEADER-BYGGARE
' ############################################################################

Private Function BuildHeader(ByRef rng As Range, ByRef data As MBlankettData) As Range
    Dim doc As Document
    Set doc = rng.Document

    ' Rad 1: Etiketter (TILL / FRAN / TID)
    Dim rLabel1 As Range
    Set rLabel1 = rng.Duplicate
    rLabel1.Text = "TILL" & vbTab & "FR" & ChrW$(197) & "N" & vbTab & "TID" & vbCr
    FormatAsLabel rLabel1
    SetTabStops rLabel1

    ' Rad 2: Varden
    Dim rValue1 As Range
    Set rValue1 = doc.Range(rLabel1.End, rLabel1.End)
    rValue1.Text = SafeValue(data.Till) & vbTab & SafeValue(data.Fran) & vbTab & SafeValue(data.Tid) & vbCr
    FormatAsValue rValue1
    SetTabStops rValue1

    ' Rad 3: Etikett (AMNE)
    Dim rLabel2 As Range
    Set rLabel2 = doc.Range(rValue1.End, rValue1.End)
    rLabel2.Text = ChrW$(196) & "MNE" & vbCr
    FormatAsLabel rLabel2

    ' Rad 4: Amne-varde
    Dim rValue2 As Range
    Set rValue2 = doc.Range(rLabel2.End, rLabel2.End)
    rValue2.Text = SafeValue(data.Amne) & vbCr
    FormatAsValue rValue2
    rValue2.Font.Bold = True

    ' Avdelare (heldragen linje)
    Dim rSep As Range
    Set rSep = doc.Range(rValue2.End, rValue2.End)
    rSep.Text = vbCr
    With rSep.Paragraphs(1)
        .SpaceBefore = 4
        .SpaceAfter = 6
        .Format.Borders(wdBorderBottom).LineStyle = wdLineStyleSingle
        .Format.Borders(wdBorderBottom).LineWidth = wdLineWidth150pt
        .Format.Borders(wdBorderBottom).Color = vbBlack
    End With

    Set BuildHeader = doc.Range(rSep.End, rSep.End)

    Set rLabel1 = Nothing
    Set rValue1 = Nothing
    Set rLabel2 = Nothing
    Set rValue2 = Nothing
    Set rSep = Nothing
    Set doc = Nothing
End Function


' ############################################################################
'  BODY-BYGGARE
' ############################################################################

Private Function BuildBody(ByRef rng As Range, ByRef data As MBlankettData) As Range
    Dim doc As Document
    Set doc = rng.Document

    Dim rBody As Range
    Set rBody = doc.Range(rng.Start, rng.Start)

    If Len(data.Bodytext) > 0 Then
        Dim sText As String
        sText = Replace(data.Bodytext, vbLf, vbCr)
        sText = Replace(sText, vbCr & vbCr & vbCr, vbCr & vbCr)
        rBody.Text = sText & vbCr
    Else
        rBody.Text = vbCr
    End If

    FormatAsBody rBody

    ' Signatur
    If Len(Trim$(data.Sign)) > 0 Then
        Dim rSign As Range
        Set rSign = doc.Range(rBody.End, rBody.End)
        rSign.Text = vbCr & vbCr & data.Sign & vbCr
        With rSign.Font
            .Name = "Arial"
            .Size = BODY_FONT_SIZE
            .Color = vbBlack
            .Bold = False
        End With
        With rSign.ParagraphFormat
            .SpaceBefore = 12
            .SpaceAfter = 0
            .LeftIndent = CentimetersToPoints(BODY_LEFT_INDENT_CM)
            .LineSpacingRule = wdLineSpaceSingle
        End With
        Set BuildBody = doc.Range(rSign.End, rSign.End)
        Set rSign = Nothing
    Else
        Set BuildBody = doc.Range(rBody.End, rBody.End)
    End If

    Set rBody = Nothing
    Set doc = Nothing
End Function


' ############################################################################
'  FORMATERINGS-HJALPARE
' ############################################################################

Private Sub FormatAsLabel(ByRef rng As Range)
    With rng.Font
        .Name = "Arial"
        .Size = LABEL_FONT_SIZE
        .AllCaps = True
        .Color = LABEL_FONT_COLOR
        .Bold = False
    End With
    With rng.ParagraphFormat
        .SpaceBefore = 2
        .SpaceAfter = 0
        .LineSpacingRule = wdLineSpaceSingle
    End With
End Sub

Private Sub FormatAsValue(ByRef rng As Range)
    With rng.Font
        .Name = "Arial"
        .Size = VALUE_FONT_SIZE
        .AllCaps = False
        .Color = vbBlack
        .Bold = False
    End With
    With rng.ParagraphFormat
        .SpaceBefore = 0
        .SpaceAfter = 2
        .LineSpacingRule = wdLineSpaceSingle
    End With
End Sub

Private Sub FormatAsBody(ByRef rng As Range)
    With rng.Font
        .Name = "Arial"
        .Size = BODY_FONT_SIZE
        .Color = vbBlack
        .Bold = False
        .AllCaps = False
    End With
    With rng.ParagraphFormat
        .SpaceBefore = 0
        .SpaceAfter = 6
        .LeftIndent = CentimetersToPoints(BODY_LEFT_INDENT_CM)
        .LineSpacingRule = wdLineSpaceSingle
        .Alignment = wdAlignParagraphLeft
    End With
End Sub

Private Sub SetTabStops(ByRef rng As Range)
    With rng.ParagraphFormat
        .TabStops.ClearAll
        .TabStops.Add Position:=CentimetersToPoints(TAB_COL2_CM), _
                       Alignment:=wdAlignTabLeft
        .TabStops.Add Position:=CentimetersToPoints(TAB_COL3_CM), _
                       Alignment:=wdAlignTabLeft
    End With
End Sub

Private Function SafeValue(ByVal sVal As String) As String
    If Len(Trim$(sVal)) = 0 Then
        SafeValue = Chr$(8212)  ' Em-dash som platshallare
    Else
        SafeValue = sVal
    End If
End Function
