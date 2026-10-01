#ifndef AppVersion
  #define AppVersion "2.0.0-alpha.1"
#endif
#ifndef FileVersion
  #define FileVersion "2.0.0.1"
#endif
#ifndef RepoRoot
  #define RepoRoot AddBackslash(SourcePath) + "..\.."
#endif

[Setup]
AppId={{097487D9-FA11-47A1-B2C6-6906858C2E78}
AppName=IMS Workbench
AppVersion={#AppVersion}
VersionInfoVersion={#FileVersion}
AppPublisher=IMS Projekt
AppPublisherURL=https://github.com/junker-joerg/ims
DefaultDirName={localappdata}\Programs\IMS Workbench
DefaultGroupName=IMS Workbench
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0.22000
OutputDir={#RepoRoot}\dist\installer
OutputBaseFilename=IMS-Setup-{#AppVersion}-win-x64
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
UninstallDisplayName=IMS Workbench
CloseApplications=yes
RestartApplications=no
SetupMutex=IMSWorkbenchSetup

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Files]
Source: "{#RepoRoot}\dist\IMS-Workbench\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\IMS Workbench"; Filename: "{app}\IMS-Workbench.exe"
Name: "{group}\IMS beenden"; Filename: "{app}\IMS-Workbench.exe"; Parameters: "--stop"
Name: "{group}\Bestehende IMS-Daten übernehmen"; Filename: "{app}\IMS-Workbench.exe"; Parameters: "--choose-import"
Name: "{group}\Hilfe"; Filename: "{app}\_internal\resources\help.html"
Name: "{group}\IMS deinstallieren"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\IMS-Workbench.exe"; Description: "IMS Workbench starten"; Flags: nowait postinstall skipifsilent

[Code]
function StopIMS(): Boolean;
var
  Code: Integer;
  ExePath: String;
begin
  ExePath := ExpandConstant('{app}\IMS-Workbench.exe');
  Result := True;
  if FileExists(ExePath) then
    Result := Exec(ExePath, '--stop --headless', '', SW_HIDE, ewWaitUntilTerminated, Code) and (Code = 0);
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  Result := '';
  if not StopIMS() then
    Result := 'IMS antwortet nicht. Bitte IMS über sein Fenster beenden und erneut installieren.';
end;

function InitializeUninstall(): Boolean;
begin
  Result := StopIMS();
  if not Result then
    MsgBox('IMS bitte über sein Fenster beenden und erneut deinstallieren.', mbError, MB_OK);
end;

// No UninstallDelete entries: AppData user data and backups are never removed.
