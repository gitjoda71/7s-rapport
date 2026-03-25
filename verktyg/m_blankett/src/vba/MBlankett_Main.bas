Attribute VB_Name = "MBlankett_Main"
Option Explicit

' ============================================================================
' MBlankett_Main
' Ansvar: Huvudmakro som orkestrerar hela M-blankett-genereringen.
' Anvandaren klistrar in ratext, kor makrot, och far en formaterad blankett.
'
' Beroenden: MBlankett_Parser, MBlankett_Header, MBlankett_Body
' ============================================================================

' ----------------------------------------------------------------------------
' SkapaMBlankett
' Huvudrutin - anropas via knapp eller kortkommando i Word.
' 1. Laser hela dokumentets text
' 2. Rensar dokumentet
' 3. Konfigurerar sidlayout
' 4. Parsar ratexten
' 5. Bygger header och body
' ----------------------------------------------------------------------------
Public Sub SkapaMBlankett()
    On Error GoTo ErrorHandler

    Dim doc As Document
    Set doc = ActiveDocument

    ' --- Steg 1: Hamta ratext ---
    Dim sRawText As String
    sRawText = doc.Content.Text

    If Len(Trim$(sRawText)) = 0 Then
        MsgBox "Dokumentet ar tomt. Klistra in din ratext och kor makrot igen.", _
               vbInformation, "M-blankett"
        GoTo CleanUp
    End If

    ' --- Steg 2: Rensa dokumentet ---
    doc.Content.Text = ""

    ' --- Steg 3: Sidlayout ---
    ConfigurePageSetup doc

    ' --- Steg 4: Parsa ---
    Dim data As MBlankettData
    data = ParseText(sRawText)

    ' --- Steg 5: Bygg header ---
    Dim rng As Range
    Set rng = doc.Range(0, 0)
    Set rng = BuildHeader(rng, data)

    ' --- Steg 6: Bygg body ---
    Set rng = BuildBody(rng, data)

    ' Flytta markoren till borjan
    doc.Range(0, 0).Select

CleanUp:
    Set rng = Nothing
    Set doc = Nothing
    Exit Sub

ErrorHandler:
    MsgBox "Ett ovantad fel uppstod: " & Err.Description & vbCrLf & _
           "(Felkod: " & Err.Number & ")", _
           vbExclamation, "M-blankett - Fel"
    Resume CleanUp
End Sub

' ----------------------------------------------------------------------------
' ConfigurePageSetup - Staller in sidmarginaler och orientering
' ----------------------------------------------------------------------------
Private Sub ConfigurePageSetup(ByRef doc As Document)
    With doc.PageSetup
        .Orientation = wdOrientPortrait
        .TopMargin = CentimetersToPoints(2)
        .BottomMargin = CentimetersToPoints(2)
        .LeftMargin = CentimetersToPoints(2.5)
        .RightMargin = CentimetersToPoints(2.5)
    End With
End Sub
