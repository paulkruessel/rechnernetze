\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{kdiartcl}[2019/10/22 Article Erweiterungen fuer Konzepte der Informatik an der Uni Konstanz]
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%
%% kdiartcl ist eine Dokumentenklasse zum Anfertigen von Lösungen für "Konzepte der Informatik" und "Datenbanksysteme".
%%
%% Die ursprüngliche "Kleine LaTeX-Vorlage" wurde durch die Fachschaft Informatik Uni Konstanz bereit gestellt.
%% https://www.fachschaft.inf.uni-konstanz.de/hilfreichelinks/
%% Mittlerweile wurde die Vorlage so umfangreich, dass sich eine Ausgliederung in eine Dokumentenklasse angeboten hat.
%%
%%
%% Änderungshistorie:
%%
%% [2019/10/22] Manuel Hotz -- Auslagerung in Dokumentenklasse kdiartcl, 
%%                             Verbesserungen der Def. des Titels/Header/Footer, kleinere Anpassungen der Dokumentation
%% [2018/11/09] Manuel Hotz -- Beispiel mittels algorithm2e an Vorlesung angepasst, konsistenteres Schriftbild, ausführlichere Dokumentation
%% [2018/11/06] Manuel Hotz -- Binärbaum-Beispiel, Neues Pseudocode-Paket (`algpseudocode`) und großes Beispiel,
%%                             TikZ-Paket `positioning` hinzugefügt
%% [2018/11/05] Manuel Hotz -- Möglichkeit Gruppen-Nummer oben auf das Blatt zu schreiben
%% [2018/04/26] Manuel Hotz -- Kleinere Änderungen für Datenbanksysteme 2018
%% [2017/10/23] Manuel Hotz -- Kleinere Änderungen für Konzepte der Informatik WS 17/18
%% [2016/11/16] Manuel Hotz -- Änderungen für Gruppe B in Konzepte der Informatik WS 16/17
%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%
%% Installation:
%% 
%% MiKTeX: https://docs.miktex.org/2.9/manual/localadditions.html
%% --> "Register a user-managed TEXMF root directory"
%% --> Dann die Klasse in diesen Ordner verschieben
%%    mehr Hinweise: https://tex.stackexchange.com/a/69484
%%    und https://texfaq.org/FAQ-inst-wlcf
%%
%% TeX Live (& MacTeX?)
%% https://texfaq.org/FAQ-install-where
%% https://texfaq.org/FAQ-inst-wlcf
%% 
%% --> Kopieren in $TEXMF/tex/latex/kdiartcl/
%% --> evtl texhash ausführen
%%
%%
%% ODER im selben Verzeichnis wie das Dokument lassen
%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% Minimales Beispiel
%% \documentclass{kdiartcl}
%% \university{Universität Konstanz}
%% \institute{Fachbereich Informatik \& Informationswissenschaft}
%% \lecture{Konzepte der Informatik}
%% \semester{Wintersemester 2019/2020}
%% \date{\today}
%% \group{1. PG}
%% \title{Lösung des 99. Aufgabenblattes}
%% \subtitle{Deadline: Tag, Datum, Uhrzeit}
%% \author{R. Rivest \and A. Shamir \and L. Adleman}
%% \begin{document}
%% \maketitle
%% \LaTeX
%% \end{document}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Die Dokumentenklasse steuert generelles Aussehen (Layout, Schrift, usw. usf.)
%% Das Layout kann mittles Paket "geometry" verändert werden.
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\LoadClass[12pt, a4paper]{article}
%%
%% Jetzt geht es mit einer kleinen Anpassung des Layouts los
%% Formatierung der Seite damit wir mehr Platz haben
\usepackage[
  height=22cm, % erweiterte Textblock-Höhe für DIN A4
  %showframe, % zum Layout-Debuggen aktivieren
  top=7\baselineskip, % Distanz des Textblockes vom oberen Seitenrand
  headheight=3\baselineskip, % 3 Zeilen Header,
  heightrounded, % Ganzzahlige Anzahl Zeilen
  headsep=2\baselineskip, % zwischen Header und Text zwei Zeilen Platz
]{geometry}
\setlength{\parindent}{0mm} % Paragrapheinrückung entfernen
%%
\usepackage[absolute, overlay]{textpos} % für absolute Positionierungen
\setlength{\TPHorizModule}{1mm} % von textpos
\setlength{\TPVertModule}{1mm} % von textpos
%% Nun brauchen wir noch ansprechende Header/Footer
\usepackage{fancyhdr}
\pagestyle{fancy} % Aktiviere fancy Stil
\usepackage{titling} % für Befehle wie \thetitle, \theauthor trotz \maketitle 
%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Pakete für Umlaute, Rechtschreibung und Orthographie
%%
\usepackage[english,ngerman]{babel} % Neue deutsche Rechtschreibung, für primär englischen Text Reihenfolge tauschen
%% Seit TeXLive 2018 ist utf8 das default inputenc
% \usepackage[utf8]{inputenc} % Eingabeencoding (nicht verwechseln mit Dateiencoding im Editor),
%%                             ermöglicht direkte Verwendung von Umlauten im TeX
%%
\usepackage[T1]{fontenc} % Neues LaTeX Schriftart-Encoding für korrekte Darstellung von Umlauten im PDF 
%%                       % z.B. richtige Glyphen anstatt Kombination aus ¨ und Buchstaben
%%                       % Es wird nun UTF8 für Glyphen verwendet
\usepackage{textcomp} % Für richtige Upperquotes in Programmcode-Listings ohne Probleme bei Copy&Paste
\usepackage[babel]{csquotes} % Richtige Anführungszeichen leicht gemacht: \enquote{Text in Anführungszeichen} statt Kombinationen aus `` und ''.
\usepackage{epigraph} % Blockzitate (wie sie in vielen Büchern am Anfang gefunden werden)
\usepackage[
  babel=true,
  expansion=alltext,
  protrusion=alltext-nott,
  final
]{microtype} % kleine Darstellungsfixes für Textsatz, generell zu empfehlen aber optional
\usepackage[doublespacing]{setspace} % anstatt \baselinestretch und \linespread verwenden wir ein Paket, das Abstände in Fußnoten
%%                    % und Listenumbgebungen in Ruhe lässt
%\doublespacing % für komfortable Korrekturanmerkungen; alternativ: \onehalfspacing \singlespacing
%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Pakete für moderne Schriftarten
%%
\usepackage{sourcecodepro} % für Source Code (listings) und \texttt
\usepackage[
  %default % falls aktiviert wird Source Serif Pro als Default-Schriftart (Hauptfont) verwendet
]{sourceserifpro} % für serife Schrift, wie sie z.B. im Mathemodus zu sehen ist
\usepackage[
  %default % falls aktiviert wird Source Sans Pro als Default-Schriftart (Hauptfont) _und_ als SansSerif-Schriftart gesetzt
]{sourcesanspro} % sans-serif
\usepackage{sectsty} % Sections in ...
\allsectionsfont{\sffamily} % ... serifenloser Schrift
%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Pakete für mathematischen Formelsatz
%%
\usepackage{amsmath}  % Verbesserungen für mathematischen Formelsatz (viele hilfreiche, moderne Umgebungen)
\usepackage{amssymb}  % Erweiterte mathematische Symbole, lädt Paket 'amsfonts'
\usepackage{amsthm}   % Theoremumgebungen
\usepackage{marvosym} % Mehr Symbole. Zum Beispiel: Euro-Zeichen, Warnhinweise, usw. usf.
%%
%% weitere Informationen: http://tex.stackexchange.com/a/32102
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Pakete für Farben und Tabellen
%%
\usepackage{multirow} % Für Tabellen
\usepackage[table, xcdraw]{xcolor} % Viele Farben und Optionen für Tabellen
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Pakete für Links und Grafiken
\usepackage[
  colorlinks=true, % farbige Links aktivieren
  urlcolor=blue, % blaue Hyperlinks
  citecolor=black % schwarze Referenzen
]{hyperref} % Hyperlinks mit blauer Schrift
\usepackage{graphicx} % Einbinden von Grafiken mittels \includegraphics (JPEG, PNG, SVG, ...)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Alle unsere Float-Umgebungen mit konsistentem Aussehen versehen
\usepackage{float}
\floatstyle{ruled}
\restylefloat{figure}
\restylefloat{table}
\usepackage{caption} % Für alles, was nicht durch das Paket float schon geändert wurde
\captionsetup[lstlisting]{labelfont={bf}} % falls listings ohne float-Umgebung verwendet werden, sollte wenigstens das label fettgedruckt werden
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Pakete für Source Code, Pseudocode/Algorithmen und Struktogramme
%%
\newfloat{Programmcode}{htbp}{code} % newfloat aus Paket float, konsistente Darstellung und eigene Zähler
\newfloat{Algorithmus}{htbp}{algo} % newfloat aus Paket float, konsistente Darstellung und eigene Zähler

%%%%%%%%%% PROGRAMMCODE
%%
\usepackage{listings} % Darstellung/Einbinden von Source Code (Snippets, Segments, Files)
\renewcommand{\lstlistingname}{Programmcode}
%% Generelle Einstellungen
\lstset{
  language=java, % Standardsprache setzen
  morekeywords={var}, % var seit Java 11
  basicstyle=\small\ttfamily, % Schriftart für Code
  numbers=left,
  numbersep=5pt,
  numberstyle=\bfseries\fontsize{8}{10}\selectfont, % Damit Zeilennummern wie bei algorithm2e aussehen
  commentstyle=\color{black!90}\itshape,
  breaklines=true, % automatischer Zeilenumbruch
  breakatwhitespace=false, % automatischer Zeilenumbruch nur an whitespace
  extendedchars=true,
  upquote=true,
  escapechar={\%},
}
%% Wir definieren uns unsere "eigene" Programmiersprache (in diesem Fall ein SQL-Dialekt der viele Schlüsselworte von PostgreSQL beinhaltet)
\lstdefinelanguage{PostgreSQL}{
  language=sql,
  morekeywords={*,SCHEMA,DATABASE,FETCH,ROW,WITH,REFERENCES,TEXT,TINYINT,GROUPING,SETS,MODIFY,...},
  moredelim=**[is][\color{red}]{<@}{@>},
  showstringspaces=true,
}

%% Einbinden von Code-Dateien (sehr flexibel!):
%% \lstinputlisting[language=Java]{name.java}
%% Code Snippets: \lstinline{foo}

%%%%%%%%%% ALGORITHMEN
%%

%%% Pseudocode mittels algorithm2e
\usepackage[
vlined, % Linien
linesnumbered, % Nummerierte Zeilen
commentsnumbered, % Kommentarzeilen sollen auch Nummeriert werden
]{algorithm2e}
%%% algorithm2e Konfiguration
\DontPrintSemicolon
\SetAlgoInsideSkip{medskip} % ein bisschen mehr Platz zwischen den Linien

%%%%%%%%%% Schriftstile
%%
%% Kommentarstil (Font, Zeichen, Ort)
\newcommand\smallcomm[1]{\footnotesize\sffamily\itshape #1}
\SetCommentSty{smallcomm}
\SetSideCommentLeft
\SetKwComment{Comment}{$\triangleright\;$}{}
%% Funktionsstil
\SetFuncSty{textsc}
%% Argumentstil so wechseln, dass sie wie Variablen in der Mathemodus-Schriftart gesetzt werden
%% falls die Serifen-Font oben geändert wurde, muss hier auch die entsprechende Font ausgewählt werden...
%% Falls es hier einen einfacheren Weg gibt, bitte melden!
\newcommand\argfont[1]{\fontfamily{SourceSerifPro-TLF}\selectfont \itshape #1}
\SetArgSty{argfont}
\SetKwProg{Procedure}{procedure}{}{} % Prozeduren heißen bei uns so
%%%

%%%%%%%%%% STRUKTOGRAMME
\usepackage[
ngerman % Option für definierte Werte wie \sTrue
% english % English option
]{struktex} % Nassi-Shneiderman Diagramme
%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Zeichnen und Farben
%%
\usepackage{tikz} % Paket für vektorisiertes, prozedurales Zeichnen (und so viel mehr!)
% TikZ bietet viele nützliche Bibliotheken, die wir verwenden können (einfach das Kommentarzeichen entfernen)
\usetikzlibrary{
  %arrows,            % Viele verschiedene Spitzen-Typen für Pfeile (mehr: http://tex.stackexchange.com/a/42679)
  automata,           % Zeichnen von Automaten
  %backgrounds,       % Hintergründe ändern
  chains,             % Abläufe darstellen
  %matrix,            % Matrizen malen
  %shadows,           % Schatten um Formen
  shapes,             % Alle zusätzlichen Formen
  %shapes.geometric,  % Mehr geometrische Formen
  %shapes.symbols,    % Mehr symbolische Formen
  %shapes.arrows,     % Mehr Pfeilformen (nicht zu verwechseln mit den Pfeilen für Pfade)
  %shapes.multipart,  % Formen unterteilen
  %shapes.callouts,   % Z.b. Sprechblasen wie man sie aus Comics kennt
  %shapes.misc,       % Diverse andere Formen, z.B. durchgestrichene Formen (crossout, strikeout)
  %spy,               % "Genaueres Hinsehen" in Diagrammen verdeutlichen
  trees,              % Bäume zeichnen
  positioning         % Positionierung von Shapes, z.B. mittels "right=of ⟨node⟩"
}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Hilfreiche Kommandos könnte man sich auch definieren
%% zum Beispiel wenn man etwas oft schreiben muss.
%% Das geschieht mittels \newcommand oder \renewcommand
%% Um Abstand hinter dem Befehl zu erzeugen, sollten auch Befehle ohne Parameter mit folgenden geschweiften Klammern
%% verwendet werden, z.B. \myCmd{} 

% Als Beispiel definieren wir uns ein paar Landau-Symbole
\newcommand{\bigO}{\ensuremath{\mathcal{O}}}
\newcommand{\bigOm}{\ensuremath{\Omega}}
\newcommand{\bigT}{\ensuremath{\Theta}}
\newcommand{\smallO}{\ensuremath{o}}
\newcommand{\smallOm}{\ensuremath{\omega}}


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Titel / Header / Footer
%% Hier muss eigentlich nichts verändert werden.
%% Da wir auch auf interne Variablen zugreifen (die mit @), muss das hier zwischen makeatletter und makeatother geschehen.
%% Ein eigenes @maketitle, damit wir Kontrolle über pagestyle haben und die Gruppen-Nummer in die Ecke schreiben können
\renewcommand\@maketitle{%
\begin{textblock}{24}(190,14)
  \textcolor{red}{ \bfseries \Large \@group }
\end{textblock}
\begin{center}%
  \par{\LARGE\bfseries\sffamily \@title}%
  \par{\itshape \@subtitle}
\end{center}%
}
%% Wir missbrauchen den standardmässig vorhandenen Stil 'plain' (automatisch auf Seite von \maketitle)
%% mit vielen Informationen zum Zuordnen der Abgabe
\fancypagestyle{plain}{ %
  \fancyhf{}% Header/Footer löschen
  \fancyhead[L]{%
  \footnotesize\scshape%
  \@university\\
  \@institute \\
  \itshape \theauthor
  }
  \fancyhead[R]{%
  \footnotesize\scshape
  \@lecture \\
  \@semester \\
  \thedate
  }
  \fancyfoot[C]{\footnotesize Seite \thepage}
  \renewcommand{\headrulewidth}{0pt}
  \renewcommand{\footrulewidth}{0pt}
}
%% ... und nun auch noch den vorhandenen normalerweise verwendeten Stil 'plain'
%% mit weniger Infos, damit man aber trotzdem einzelne Blätter schnell zuordnen kann
\fancyhf{}% Header/Footer löschen
\fancyfoot[C]{\footnotesize Seite \thepage}
\fancyhead[L]{%
\footnotesize
{\scshape \theauthor}
}
\fancyhead[R]{%
\footnotesize
{\scshape \@lecture}
}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\newcommand\university[1]{\renewcommand\@university{#1}}
\newcommand\@university{}
\newcommand\lecture[1]{\renewcommand\@lecture{#1}}
\newcommand\@lecture{}
\newcommand\institute[1]{\renewcommand\@institute{#1}}
\newcommand\@institute{}
\newcommand\semester[1]{\renewcommand\@semester{#1}}
\newcommand\@semester{}
\newcommand\group[1]{\renewcommand\@group{#1}}
\newcommand\@group{}
\newcommand\subtitle[1]{\renewcommand\@subtitle{#1}}
\newcommand\@subtitle{}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


\endinput