#ifndef MyAppName
  #define MyAppName "CSPdv"
#endif
#ifndef MyAppVersion
  #define MyAppVersion "1.0.0"
#endif
#ifndef MyAppPublisher
  #define MyAppPublisher "CSPdv"
#endif
#ifndef MyAppExeName
  #define MyAppExeName "CSPdv.exe"
#endif

[Setup]
AppId={{E97A85B9-1C8C-4B5D-9C4A-69C07A7A38B8}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\dist-installer
OutputBaseFilename=Setup_CSPdv
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupLogging=yes

[Languages]
Name: "portuguesebrazil"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na area de trabalho"; GroupDescription: "Atalhos:"
Name: "openenv"; Description: "Abrir configuracao (.env) ao finalizar"; GroupDescription: "Pos-instalacao:"; Flags: checkedonce
Name: "openfolder"; Description: "Abrir pasta de instalacao ao finalizar"; GroupDescription: "Pos-instalacao:"

[Files]
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\.env.example"; DestDir: "{app}"; DestName: ".env.example"; Flags: ignoreversion
Source: "..\.env.example"; DestDir: "{app}"; DestName: ".env"; Flags: onlyifdoesntexist
Source: "LEIAME_INSTALACAO.txt"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "notepad.exe"; Parameters: """{app}\.env"""; Description: "Abrir arquivo .env para configurar o banco"; Flags: postinstall skipifsilent; Tasks: openenv
Filename: "explorer.exe"; Parameters: """{app}"""; Description: "Abrir pasta de instalacao"; Flags: postinstall skipifsilent; Tasks: openfolder
Filename: "{app}\{#MyAppExeName}"; Description: "Executar {#MyAppName}"; Flags: nowait postinstall skipifsilent
