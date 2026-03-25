Attribute VB_Name = "MBlankett_Header"
Option Explicit

' ============================================================================
' MBlankett_Header
' Ansvar: Bygga upp M-blankettens sidhuvud (header) i Word-dokumentet.
' Anvander Range-objekt och TabStops for att linjera falt.
' ============================================================================

' Layout-konstanter (centimeter, konverteras till Points via CentimetersToPoints)
Private Const TAB_COL2_CM As Single = 7     ' Mittkolumn (FRAN)
Private Const TAB_COL3_CM As Single = 13    ' Hogerkolumn (TID)

Private Const LABEL_FONT_SIZE As Single = 8
Private Const VALUE_FONT_SIZE As Single = 11
Private Const LABEL_FONT_COLOR As Long = 5263440  ' RGB(80,80,80)

' ----------------------------------------------------------------------------
' BuildHeader
' Tar ett Range-objekt (start av dokumentet) och en MBlankettData-struktur.
' Skriver in headerfalt med etiketter och varden pa tva rader:
'   Rad 1: TILL [tab] FRAN [tab] TID        (etiketter)
'   Rad 2: <till-varde> [tab] <fran-varde> [tab] <tid-varde>
'   Rad 3: AMNE (etikett)
'   Rad 4: <amne-varde>
'   [avdelare - heldragen linje]
'
' Returnerar Range-positionen efter headern.
' ----------------------------------------------------------------------------
Public Function BuildHeader(ByRef rng As Range, ByRef data As MBlankettData) As Range
    Dim doc As Document
    Set doc = rng.Document

    ' --- Rad 1: Etiketter (TILL / FRAN / TID) ---
    Dim rLabel1 As Range
    Set rLabel1 = rng.Duplicate
    rLabel1.Text = "TILL" & vbTab & "FR" & ChrW$(197) & "N" & vbTab & "TID" & vbCr

    FormatAsLabel rLabel1
    SetTabStops rLabel1

    ' --- Rad 2: Varden ---
    Dim rValue1 As Range
    Set rValue1 = doc.Range(rLabel1.End, rLabel1.End)
    rValue1.Text = SafeValue(data.Till) & vbTab & SafeValue(data.Fran) & vbTab & SafeValue(data.Tid) & vbCr

    FormatAsValue rValue1
    SetTabStops rValue1

    ' --- Rad 3: Etikett (AMNE) ---
    Dim rLabel2 As Range
    Set rLabel2 = doc.Range(rValue1.End, rValue1.End)
    rLabel2.Text = ChrW$(196) & "MNE" & vbCr

    FormatAsLabel rLabel2

    ' --- Rad 4: Amne-varde ---
    Dim rValue2 As Range
    Set rValue2 = doc.Range(rLabel2.End, rLabel2.End)
    rValue2.Text = SafeValue(data.Amne) & vbCr

    FormatAsValue rValue2
    ' Gör ämnet fetstilt
    rValue2.Font.Bold = True

    ' --- Avdelare (heldragen linje under sista header-raden) ---
    Dim rSep As Range
    Set rSep = doc.Range(rValue2.End, rValue2.End)
    rSep.Text = vbCr  ' Tomt stycke som bär kantlinjen

    With rSep.Paragraphs(1)
        .SpaceBefore = 4
        .SpaceAfter = 6
        .Format.Borders(wdBorderBottom).LineStyle = wdLineStyleSingle
        .Format.Borders(wdBorderBottom).LineWidth = wdLineWidth150pt
        .Format.Borders(wdBorderBottom).Color = vbBlack
    End With

    ' Returnera position efter headern
    Set BuildHeader = doc.Range(rSep.End, rSep.End)

    ' Stadning
    Set rLabel1 = Nothing
    Set rValue1 = Nothing
    Set rLabel2 = Nothing
    Set rValue2 = Nothing
    Set rSep = Nothing
    Set doc = Nothing
End Function

' ----------------------------------------------------------------------------
' FormatAsLabel - Applicera etikett-formatering (sma versaler, gra)
' ----------------------------------------------------------------------------
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

' ----------------------------------------------------------------------------
' FormatAsValue - Applicera varde-formatering (normal storlek, svart)
' ----------------------------------------------------------------------------
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

' ----------------------------------------------------------------------------
' SetTabStops - Konfigurera tabb-stopp for flerkolumnsrader
' ----------------------------------------------------------------------------
Private Sub SetTabStops(ByRef rng As Range)
    With rng.ParagraphFormat
        .TabStops.ClearAll
        .TabStops.Add Position:=CentimetersToPoints(TAB_COL2_CM), _
                       Alignment:=wdAlignTabLeft
        .TabStops.Add Position:=CentimetersToPoints(TAB_COL3_CM), _
                       Alignment:=wdAlignTabLeft
    End With
End Sub

' ----------------------------------------------------------------------------
' SafeValue - Returnerar vardet eller ett streck om tomt
' ----------------------------------------------------------------------------
Private Function SafeValue(ByVal sVal As String) As String
    If Len(Trim$(sVal)) = 0 Then
        SafeValue = Chr$(8212)  ' Em-dash som platshallare
    Else
        SafeValue = sVal
    End If
End Function
