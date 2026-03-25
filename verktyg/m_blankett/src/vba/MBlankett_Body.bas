Attribute VB_Name = "MBlankett_Body"
Option Explicit

' ============================================================================
' MBlankett_Body
' Ansvar: Skriva in brodtexten och signatur i M-blanketten.
' ============================================================================

Private Const BODY_FONT_SIZE As Single = 11
Private Const BODY_LEFT_INDENT_CM As Single = 0.5

' ----------------------------------------------------------------------------
' BuildBody
' Tar ett Range-objekt (position efter headern) och brodtext + signatur.
' Skriver in texten med korrekt formatering.
' Returnerar Range-positionen efter body.
' ----------------------------------------------------------------------------
Public Function BuildBody(ByRef rng As Range, ByRef data As MBlankettData) As Range
    Dim doc As Document
    Set doc = rng.Document

    ' --- Brodtext ---
    Dim rBody As Range
    Set rBody = doc.Range(rng.Start, rng.Start)

    If Len(data.Bodytext) > 0 Then
        ' Konvertera LF till CR for Word-stycken
        Dim sText As String
        sText = Replace(data.Bodytext, vbLf, vbCr)
        ' Undvik dubbla CR
        sText = Replace(sText, vbCr & vbCr & vbCr, vbCr & vbCr)

        rBody.Text = sText & vbCr
    Else
        rBody.Text = vbCr  ' Tomt stycke om ingen brodtext
    End If

    FormatAsBody rBody

    ' --- Signatur ---
    If Len(Trim$(data.Sign)) > 0 Then
        Dim rSign As Range
        Set rSign = doc.Range(rBody.End, rBody.End)

        ' Lagg till lite avstand fore signaturen
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

    ' Stadning
    Set rBody = Nothing
    Set doc = Nothing
End Function

' ----------------------------------------------------------------------------
' FormatAsBody - Applicera brodtext-formatering
' ----------------------------------------------------------------------------
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
