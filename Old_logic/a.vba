Sub ListSubfolders()

    ' Prompt user to select root folder
    Dim rootFolder As String
    rootFolder = InputBox("Enter path to root folder:", "Select Root Folder", "E:\0")
    
    ' Create FileSystemObject
    Dim fso As Object
    Set fso = CreateObject("Scripting.FileSystemObject")
    
    ' Check if root folder exists
    If Not fso.FolderExists(rootFolder) Then
        MsgBox "Root folder does not exist."
        Exit Sub
    End If
    
    ' Initialize table headers and row counter
    Range("A1").Value = "Directory"
    Range("B1").Value = "Size"
 
   Range("C1").Value = "4rd Level Subdirectories"
    Range("D1").Value = "5th Level Subdirectories"
    Range("E1").Value = "6th Level Subdirectories"
    Range("F1").Value = "7th Level Subdirectories"
    Range("G1").Value = "8th Level Subdirectories"
    Range("H1").Value = "9th Level Subdirectories"
    Range("I1").Value = "Created Date"
    Range("J1").Value = "Modified Date"

    Dim row As Integer
    row = 1
    
    ' Loop through 2nd level subfolders
    ' Loop through 2nd level subfolders


Dim subRoot1 As Object
Dim subRoot2 As Object
Dim subRoot3 As Object
Dim subRoot4 As Object
Dim subRoot5 As Object
Dim subRoot6 As Object
Dim subRoot7 As Object
Dim subRoot8 As Object
Dim subRoot9 As Object
Dim subRoot10 As Object

Dim size As Double
Dim createdDate As Date
Dim modifiedDate As Date
Dim accessedDate As Date
Dim subFolders As String
Dim filesCount As Long
Dim sub5 As String
Dim sub6 As String
Dim sub7 As String
Dim sub8 As String
Dim sub9 As String
Dim sub10 As String


For Each subRoot1 In fso.GetFolder(rootFolder).SubFolders
    For Each subRoot2 In subRoot1.SubFolders
      For Each subRoot3 In subRoot2.SubFolders
        ' size = fso.GetFolder(subRoot3).Size
        createdDate = fso.GetFolder(subRoot3).DateCreated
        modifiedDate = fso.GetFolder(subRoot3).DateLastModified
        accessedDate = fso.GetFolder(subRoot3).DateLastAccessed
        subFolders = ""
        filesCount = fso.GetFolder(subRoot3).Files.Count
        
        sub5 = ""
        sub6 = ""
        sub7 = ""
        sub8 = ""
        sub9 = ""
       
        ' Loop through 4rd level subfolders
        For Each subRoot4 In subRoot3.SubFolders
            subFolders = subFolders & subRoot4.Name & ", "
            
            ' Loop through 5th level subfolders
            For Each subRoot5 In subRoot4.SubFolders
                sub5 = sub5 & subRoot5.Name & ", "
                
                ' Loop through 6th level subfolders
                For Each subRoot6 In subRoot5.SubFolders
                    sub6 = sub6 & subRoot6.Name & ", "
                    
                    ' Loop through 7th level subfolders
                    For Each subRoot7 In subRoot6.SubFolders
                        sub7 = sub7 & subRoot7.Name & ", "
                        
                        ' Loop through 8th level subfolders
                        For Each subRoot8 In subRoot7.SubFolders
                            sub8 = sub8 & subRoot8.Name & ", "
                            
                            ' Loop through 9th level subfolders
                            For Each subRoot9 In subRoot8.SubFolders
                                sub9 = sub9 & subRoot9.Name & ", "

                            
                        Next subRoot9
                    Next subRoot8
                Next subRoot7
            Next subRoot6
        Next subRoot5
      Next subRoot4



         ' Write data to worksheet
        row = row + 1
        Cells(row, 1).Value = subRoot3.Path
        ' Cells(row, 2).Value = size
        Cells(row, 3).Value = subFolders
        Cells(row, 4).Value = sub5
        Cells(row, 5).Value = sub6
        Cells(row, 6).Value = sub7
        Cells(row, 7).Value = sub8
        Cells(row, 8).Value = sub9
        Cells(row, 9).Value = createdDate
        Cells(row, 10).Value = modifiedDate
        Cells(row, 12).Value = accessedDate
        Cells(row, 11).Value = filesCount


Next subRoot3
Next subRoot2
Next subRoot1
  ' Autofit columns
 ' Columns("A:L1").AutoFit
' Release FileSystemObject
Set fso = Nothing
    End Sub       