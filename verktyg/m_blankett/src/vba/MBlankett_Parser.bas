Attribute VB_Name = "MBlankett_Parser"
Option Explicit

' ============================================================================
' MBlankett_Parser
' Ansvar: Extrahera headerfalt och brodtext fran ratext med Regex.
' Sparas i: hv/verktyg/m_blankett/src/vba/
' ============================================================================

Public Type MBlankettData
    Till        As String
    Fran        As String
    Tid         As String
    Amne        As String
    Sign        As String
    Bodytext    As String
End Type

' ----------------------------------------------------------------------------
' ParseText
' Tar en ratext-strang och returnerar en MBlankettData-struktur.
' Logik:
'   1. Dela upp i Header-del och Body-del via "---" eller dubbel-radbrytning.
'   2. Extrahera kanda falt ur headern via Regex.
'   3. Allt efter avskiljaren hamnar i Bodytext.
'   4. SIGN: kan ligga i headern ELLER i slutet av body.
' ----------------------------------------------------------------------------
Public Function ParseText(ByVal sRawText As String) As MBlankettData
    Dim result As MBlankettData
    Dim sHeader As String
    Dim sBody As String
    Dim posDelimiter As Long

    ' Normalisera radbrytningar till vbLf
    sRawText = Replace(sRawText, vbCrLf, vbLf)
    sRawText = Replace(sRawText, vbCr, vbLf)

    ' --- Steg 1: Separera header fran body ---
    posDelimiter = InStr(1, sRawText, vbLf & "---", vbTextCompare)
    If posDelimiter = 0 Then
        posDelimiter = InStr(1, sRawText, "---" & vbLf, vbTextCompare)
    End If

    If posDelimiter > 0 Then
        sHeader = Left$(sRawText, posDelimiter - 1)
        ' Hoppa over "---" och eventuell radbrytning efter
        Dim afterDelim As Long
        afterDelim = InStr(posDelimiter, sRawText, "---")
        sBody = Mid$(sRawText, afterDelim + 3)
        ' Trimma inledande radbrytningar fran body
        Do While Left$(sBody, 1) = vbLf
            sBody = Mid$(sBody, 2)
        Loop
    Else
        ' Fallback: dubbel radbrytning som avskiljare
        Dim posDouble As Long
        posDouble = InStr(1, sRawText, vbLf & vbLf)
        If posDouble > 0 And HasHeaderFields(Left$(sRawText, posDouble)) Then
            sHeader = Left$(sRawText, posDouble - 1)
            sBody = Mid$(sRawText, posDouble + 2)
        Else
            ' Ingen struktur hittad - allt blir body
            sHeader = ""
            sBody = sRawText
        End If
    End If

    ' --- Steg 2: Extrahera falt fran header ---
    result.Till = ExtractField(sHeader, "TILL")
    result.Fran = ExtractField(sHeader, "FR" & ChrW$(197) & "N")  ' FRAN med A-ring
    If Len(result.Fran) = 0 Then
        result.Fran = ExtractField(sHeader, "FRAN")  ' Fallback utan diakritik
    End If
    result.Tid = ExtractField(sHeader, "TID")
    result.Amne = ExtractField(sHeader, "(" & ChrW$(196) & "MNE|AMNE|RUBRIK)")  ' AMNE med A-trema eller RUBRIK
    result.Sign = ExtractField(sHeader, "(SIGN|AVS SIGN|UNDERSKRIFT)")

    ' --- Steg 3: Kolla om SIGN finns i slutet av body ---
    If Len(result.Sign) = 0 Then
        result.Sign = ExtractFieldFromEnd(sBody, "(SIGN|AVS SIGN|UNDERSKRIFT)")
        If Len(result.Sign) > 0 Then
            sBody = RemoveFieldFromEnd(sBody, "(SIGN|AVS SIGN|UNDERSKRIFT)")
        End If
    End If

    result.Bodytext = Trim$(sBody)

    ParseText = result
End Function

' ----------------------------------------------------------------------------
' ExtractField - Anvander VBScript.RegExp for att hitta "FALTNAMN: varde"
' sFieldPattern kan vara ett regex-alternativ, t.ex. "(AMNE|RUBRIK)"
' ----------------------------------------------------------------------------
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

' ----------------------------------------------------------------------------
' ExtractFieldFromEnd - Soker efter falt nara slutet av texten
' ----------------------------------------------------------------------------
Private Function ExtractFieldFromEnd(ByVal sText As String, ByVal sFieldPattern As String) As String
    Dim oRegex As Object
    Dim oMatches As Object

    Set oRegex = CreateObject("VBScript.RegExp")
    oRegex.IgnoreCase = True
    oRegex.MultiLine = True
    oRegex.Pattern = sFieldPattern & ":\s*(.*?)$"

    Set oMatches = oRegex.Execute(sText)
    If oMatches.Count > 0 Then
        ' Ta sista matchningen (narmast slutet)
        ExtractFieldFromEnd = Trim$(oMatches(oMatches.Count - 1).SubMatches(0))
    Else
        ExtractFieldFromEnd = ""
    End If

    Set oMatches = Nothing
    Set oRegex = Nothing
End Function

' ----------------------------------------------------------------------------
' RemoveFieldFromEnd - Tar bort faltrad fran slutet av texten
' ----------------------------------------------------------------------------
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

' ----------------------------------------------------------------------------
' HasHeaderFields - Kontrollerar om en textsnutt innehaller kanda faltnamn
' Anvands for att avgora om dubbel-radbrytning ska tolkas som avskiljare
' ----------------------------------------------------------------------------
Private Function HasHeaderFields(ByVal sText As String) As Boolean
    Dim oRegex As Object

    Set oRegex = CreateObject("VBScript.RegExp")
    oRegex.IgnoreCase = True
    oRegex.MultiLine = True
    oRegex.Pattern = "^(TILL|FR" & ChrW$(197) & "N|FRAN|TID|" & ChrW$(196) & "MNE|AMNE|RUBRIK|SIGN|AVS SIGN):"

    HasHeaderFields = oRegex.Test(sText)

    Set oRegex = Nothing
End Function
