"""Duplicate Pair Cleaner — portable graphical interface, stdlib Tkinter only."""
from __future__ import annotations
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from gui_logic import APP_VERSION, ScanResult, scan
from theme_prefs import MODES, load_theme, save_theme, resolve_mode, recolor

NAVY = '#0B172B'
NAVY2 = '#142A43'
TEAL = '#07988B'
LIGHT = '#F4F7FA'
BORDER = '#DAE3EA'
INK = '#17283C'
MUTED = '#657589'
WHITE = '#FFFFFF'
BAD = '#A73142'
AMBER = '#93641C'
FONT = 'Segoe UI'
PRESETS = [('Music + lyrics', '.mp3', '.lrc'), ('Video + subtitles', '.mp4', '.srt'),
           ('FLAC + lyrics', '.flac', '.lrc'), ('Photo + metadata', '.jpg', '.xmp'),
           ('Audio + notes', '.wav', '.txt'), ('Custom extensions', '', '')]


def open_in_file_manager(folder: Path) -> None:
    """Open a folder without shell interpolation."""
    if sys.platform == 'win32':
        os.startfile(str(folder))
    elif sys.platform == 'darwin':
        subprocess.Popen(['open', str(folder)])
    else:
        subprocess.Popen(['xdg-open', str(folder)])


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f'Duplicate Pair Cleaner  •  v{APP_VERSION}')
        self.geometry('1180x900')
        self.minsize(920, 720)
        self.configure(bg=LIGHT)
        self.option_add('*Font', f'{{{FONT}}} 10')
        self._events: queue.Queue[tuple[str, object]] = queue.Queue()
        self._busy = False
        self._applying = False
        self._result: ScanResult | None = None
        self._selected_group = None
        self._last_backup: Path | None = None
        self._row_groups = {}
        self._theme_originals = {}
        self._active_theme = 'Light'
        self._setup_style()
        self._setup_vars()
        self._make_layout()
        self._apply_theme()
        self._mark_idle()
        self.protocol('WM_DELETE_WINDOW', self._on_close)
        self.after(90, self._drain_events)
        self.after(15000,self._refresh_system_theme)

    def _setup_style(self):
        sty = ttk.Style(self)
        if 'clam' in sty.theme_names():
            sty.theme_use('clam')
        sty.configure('DPC.Treeview', background=WHITE, fieldbackground=WHITE,
                      foreground=INK, rowheight=34, font=(FONT, 10), borderwidth=0)
        sty.map('DPC.Treeview', background=[('selected', '#DEF3EF')],
                foreground=[('selected', NAVY)])
        sty.configure('DPC.Treeview.Heading', background='#EDF3F7', foreground=NAVY,
                      relief='flat', font=(FONT, 9, 'bold'), padding=(9, 10))
        sty.configure('DPC.TCombobox', padding=6)
        sty.configure('DPC.TEntry', padding=6)
        sty.configure('DPC.TCheckbutton', background=WHITE, foreground=INK)
        sty.configure('DPC.Horizontal.TProgressbar', troughcolor='#E5ECEF', background=TEAL,
                      bordercolor=WHITE, lightcolor=TEAL, darkcolor=TEAL)

    def _theme_style(self,mode: str) -> None:
        """Apply matching ttk styles to tree, headings, entries and dropdowns."""
        sty = ttk.Style(self)
        if 'clam' in sty.theme_names():
            sty.theme_use('clam')
        c=lambda value: recolor(value,mode)
        sty.configure('DPC.Treeview', background=c(WHITE), fieldbackground=c(WHITE),
                      foreground=c(INK), rowheight=34, font=(FONT,10),borderwidth=0)
        sty.map('DPC.Treeview',background=[('selected',c('#DEF3EF'))],
                foreground=[('selected',c(INK))])
        sty.configure('DPC.Treeview.Heading',background=c('#EDF3F7'),foreground=c(INK),
                      relief='flat',font=(FONT,9,'bold'),padding=(9,10))
        sty.map('DPC.Treeview.Heading',background=[('active',c('#E9F0F5'))],
                foreground=[('active',c(INK))])
        sty.configure('DPC.TCombobox',padding=6,fieldbackground=c(WHITE),
                      background=c('#E9F0F5'),foreground=c(INK),arrowcolor=c(INK),
                      selectbackground=c('#DEF3EF'),selectforeground=c(INK))
        sty.map('DPC.TCombobox',fieldbackground=[('readonly',c(WHITE)),('disabled',c('#E9F0F5'))],
                foreground=[('readonly',c(INK)),('disabled',c(MUTED))],
                selectbackground=[('readonly',c(WHITE))],selectforeground=[('readonly',c(INK))])
        sty.configure('DPC.TEntry',padding=6,fieldbackground=c(WHITE),
                      foreground=c(INK),insertcolor=c(INK))
        sty.configure('DPC.TCheckbutton',background=c(WHITE),foreground=c(INK))
        sty.map('DPC.TCheckbutton',background=[('active',c(WHITE))],
                foreground=[('active',c(INK))])
        sty.configure('DPC.Horizontal.TProgressbar',troughcolor=c('#E5ECEF'),background=c(TEAL),
                      bordercolor=c(WHITE),lightcolor=c(TEAL),darkcolor=c(TEAL))
        sty.configure('TEntry',padding=6,fieldbackground=c(WHITE),foreground=c(INK),insertcolor=c(INK))
        sty.configure('TCombobox',padding=6,fieldbackground=c(WHITE),background=c('#E9F0F5'),
                      foreground=c(INK),arrowcolor=c(INK))
        sty.map('TCombobox',fieldbackground=[('readonly',c(WHITE)),('disabled',c('#E9F0F5'))],
                foreground=[('readonly',c(INK)),('disabled',c(MUTED))])
        try:
            self.option_add('*TCombobox*Listbox.background',c(WHITE))
            self.option_add('*TCombobox*Listbox.foreground',c(INK))
            self.option_add('*TCombobox*Listbox.selectBackground',c('#DEF3EF'))
            self.option_add('*TCombobox*Listbox.selectForeground',c(INK))
        except tk.TclError:
            pass

    @staticmethod
    def _theme_widget_color(option, value, baseline, mode):
        if mode == 'Dark' and option in ('foreground','activeforeground','insertbackground','selectforeground'):
            if value.lower() == NAVY.lower():
                return '#EAF0F8'
            if value.lower() == WHITE.lower() and baseline.get('background','').lower() == NAVY.lower():
                return '#F4FAFE'
        return recolor(value,mode)

    def _apply_theme(self) -> None:
        """Recolor existing Tk widgets using their original light color baseline."""
        mode=resolve_mode(self.theme_var.get())
        self._active_theme=mode
        self._theme_style(mode)
        options=('background','foreground','activebackground','activeforeground',
                 'insertbackground','selectbackground','selectforeground','highlightbackground')
        def walk(w):
            yield w
            for child in w.winfo_children():
                yield from walk(child)
        for widget in walk(self):
            key=str(widget)
            if key not in self._theme_originals:
                baseline={}
                for opt in options:
                    try:
                        val=widget.cget(opt)
                    except (tk.TclError,KeyError):
                        continue
                    if isinstance(val,str) and val.startswith('#'):
                        baseline[opt]=val
                self._theme_originals[key]=baseline
            updates={opt:self._theme_widget_color(opt,value,self._theme_originals[key],mode)
                     for opt,value in self._theme_originals[key].items()}
            if updates:
                try:
                    widget.configure(**updates)
                except tk.TclError:
                    pass
        self.detail.tag_configure('backup',foreground=recolor(BAD,mode))
        self.detail.tag_configure('rename',foreground=recolor('#A26A16',mode))
        self.detail.tag_configure('keep',foreground=recolor('#067E6D',mode))
        self.detail.tag_configure('heading',foreground=recolor(INK,mode))

    def _refresh_system_theme(self):
        if not self.winfo_exists():
            return
        if self.theme_var.get() == 'System' and resolve_mode('System') != self._active_theme:
            self._apply_theme()
        self.after(15000,self._refresh_system_theme)

    def _on_theme_change(self,event=None):
        # Theme switches do not clear or modify scan or file operations.
        try:
            save_theme(self.theme_var.get())
        except OSError:
            self.status_var.set('Appearance updated; preference could not be saved on this PC.')
        self._apply_theme()

    def _setup_vars(self):
        self.folder_var = tk.StringVar()
        self.main_var = tk.StringVar(value='.mp3')
        self.sidecar_var = tk.StringVar(value='.lrc')
        self.preset_var = tk.StringVar(value=PRESETS[0][0])
        self.recursive_var = tk.BooleanVar(value=False)
        self.query_var = tk.StringVar()
        self.filter_var = tk.StringVar(value='All')
        self.status_var = tk.StringVar(value='Choose a folder to begin.')
        self.theme_var = tk.StringVar(value=load_theme())
        self.stat_vars = {key: tk.StringVar(value='0') for key in ('groups','backups','renames','warnings')}
        self.query_var.trace_add('write', lambda *_: self._populate_groups())
        for variable in (self.folder_var, self.main_var, self.sidecar_var, self.recursive_var):
            variable.trace_add('write', lambda *_: self._invalidate())

    def _frame(self, parent, bg=WHITE, **kw):
        return tk.Frame(parent, bg=bg, **kw)

    def _txt(self, parent, value, size=10, bold=False, color=INK, bg=WHITE, **kw):
        return tk.Label(parent, text=value, font=(FONT, size, 'bold' if bold else 'normal'),
                        fg=color, bg=bg, **kw)

    def _btn(self, parent, value, command, primary=False, danger=False, **kw):
        bg = TEAL if primary else ('#FCEFF0' if danger else '#E9F0F5')
        fg = WHITE if primary else (BAD if danger else INK)
        return tk.Button(parent, text=value, command=command, relief='flat',
                         cursor='hand2', bg=bg, fg=fg, activebackground='#086C68' if primary else '#DCE9F2',
                         activeforeground=WHITE if primary else INK, padx=17, pady=9,
                         font=(FONT, 9, 'bold'), borderwidth=0, **kw)

    def _make_layout(self):
        header = self._frame(self, bg=NAVY, height=82)
        header.pack(fill='x')
        header.pack_propagate(False)
        self._txt(header, '◈', 31, True, '#31C6B8', NAVY).pack(side='left', padx=(31, 15), pady=10)
        titlebox = self._frame(header, bg=NAVY)
        titlebox.pack(side='left', pady=13)
        self._txt(titlebox, 'DUPLICATE PAIR CLEANER', 18, True, WHITE, NAVY).pack(anchor='w')
        self._txt(titlebox, 'Find the right copy. Keep its companion. Know exactly what changes.',
                  10, False, '#B4C8D8', NAVY).pack(anchor='w', pady=(5, 0))
        self._txt(header, f'WINDOWS DESKTOP  /  v{APP_VERSION}', 9, True, '#8DDACE', NAVY).pack(side='right',padx=(12,25))
        self.theme_combo = ttk.Combobox(header, textvariable=self.theme_var,
                                         values=MODES, state='readonly', width=9,
                                         style='DPC.TCombobox')
        self.theme_combo.pack(side='right',padx=(5,4),pady=25)
        self.theme_combo.bind('<<ComboboxSelected>>',self._on_theme_change)
        self._txt(header,'Appearance:',9,True,'#B4C8D8',NAVY).pack(side='right')

        main = self._frame(self, bg=LIGHT)
        main.pack(fill='both', expand=True, padx=25, pady=13)
        config = self._frame(main)
        config.pack(fill='x')
        self._txt(config, '01  SELECT YOUR FILES', 10, True, TEAL).pack(anchor='w',padx=22,pady=(12,6))
        pathrow = self._frame(config)
        pathrow.pack(fill='x', padx=22, pady=(0,7))
        self.folder_entry = ttk.Entry(pathrow, textvariable=self.folder_var, style='DPC.TEntry')
        self.folder_entry.pack(side='left',fill='x',expand=True,ipady=6)
        self.browse_btn = self._btn(pathrow, 'Browse folder', self._browse, primary=True)
        self.browse_btn.pack(side='left',padx=(12,0))
        self._txt(config, '02  CHOOSE MAIN + COMPANION FILE TYPES', 10, True, TEAL).pack(anchor='w',padx=22,pady=(3,6))
        settings = self._frame(config)
        settings.pack(fill='x', padx=22, pady=(0,13))
        self._txt(settings, 'Preset', 9, True).grid(row=0,column=0,sticky='w',padx=(0,11))
        self.preset_combo = ttk.Combobox(settings, textvariable=self.preset_var, state='readonly',
                                         values=[r[0] for r in PRESETS],width=23,style='DPC.TCombobox')
        self.preset_combo.grid(row=1,column=0,sticky='ew',padx=(0,15),pady=(4,0),ipady=4)
        self.preset_combo.bind('<<ComboboxSelected>>', self._preset_changed)
        self._txt(settings, 'Main extension', 9, True).grid(row=0,column=1,sticky='w')
        self.main_entry = ttk.Entry(settings,textvariable=self.main_var,width=14,style='DPC.TEntry')
        self.main_entry.grid(row=1,column=1,sticky='ew',padx=(0,15),pady=(4,0),ipady=6)
        self._txt(settings, 'Companion extension', 9, True).grid(row=0,column=2,sticky='w')
        self.side_entry = ttk.Entry(settings,textvariable=self.sidecar_var,width=14,style='DPC.TEntry')
        self.side_entry.grid(row=1,column=2,sticky='ew',padx=(0,15),pady=(4,0),ipady=6)
        self.recursive_chk = ttk.Checkbutton(settings,text='Include subfolders',variable=self.recursive_var,
                                            style='DPC.TCheckbutton')
        self.recursive_chk.grid(row=1,column=3,sticky='w',pady=(4,0))
        settings.columnconfigure(0,weight=2)
        settings.columnconfigure(1,weight=1)
        settings.columnconfigure(2,weight=1)
        settings.columnconfigure(3,weight=1)

        stats = self._frame(main, bg=LIGHT)
        stats.pack(fill='x',pady=(10,10))
        for idx,(key,caption) in enumerate([('groups','DUPLICATE GROUPS'),('backups','BACKUP FILES'),
                                             ('renames','RENAMES'),('warnings','WARNINGS')]):
            box=self._frame(stats)
            box.grid(row=0,column=idx,sticky='nsew',padx=(0 if idx == 0 else 8,0))
            self._txt(box,caption,9,True,MUTED).pack(anchor='w',padx=18,pady=(7,2))
            self._txt(box,'',21,True,NAVY,textvariable=self.stat_vars[key]).pack(anchor='w',padx=18,pady=(0,7))
            stats.columnconfigure(idx,weight=1)

        results = self._frame(main)
        results.pack(fill='both',expand=True)
        controls = self._frame(results)
        controls.pack(fill='x',padx=20,pady=(9,6))
        self._txt(controls,'03  REVIEW PROPOSED CHANGES',10,True,TEAL).pack(side='left')
        self.search_entry = ttk.Entry(controls,textvariable=self.query_var,width=28,style='DPC.TEntry')
        self.search_entry.pack(side='right',padx=(10,0),ipady=4)
        self._txt(controls,'Search files:',9,False,MUTED).pack(side='right')
        selectionbar=self._frame(results)
        selectionbar.pack(fill='x',padx=20,pady=(0,6))
        self.filter_combo=ttk.Combobox(selectionbar,textvariable=self.filter_var,state='readonly',width=20,
                                       values=['All','With companion','Without companion'],style='DPC.TCombobox')
        self.filter_combo.pack(side='left')
        self.filter_combo.bind('<<ComboboxSelected>>',lambda *_: self._populate_groups())
        self._txt(selectionbar,'Select a group to inspect every proposed file action.',9,color=MUTED).pack(side='left',padx=15)

        panes=tk.PanedWindow(results, orient='vertical', sashwidth=7, sashrelief='flat', bg='#E8EDF2')
        panes.pack(fill='both',expand=True,padx=20,pady=(0,11))
        upper=self._frame(panes)
        lower=self._frame(panes,bg='#F7FAFB')
        panes.add(upper,minsize=115,stretch='always')
        panes.add(lower,minsize=130,stretch='always')
        self.after(250, lambda: panes.sash_place(0, 0, 165) if panes.winfo_exists() else None)
        self.tree=ttk.Treeview(upper,columns=('type','actions','reason'),show='tree headings',style='DPC.Treeview',selectmode='browse')
        self.tree.heading('#0',text='FILE GROUP',anchor='w')
        self.tree.heading('type',text='COMPANION',anchor='w')
        self.tree.heading('actions',text='ACTIONS',anchor='w')
        self.tree.heading('reason',text='WHY IT WAS SELECTED',anchor='w')
        self.tree.column('#0',width=340,stretch=True)
        self.tree.column('type',width=125,stretch=False)
        self.tree.column('actions',width=105,stretch=False)
        self.tree.column('reason',width=350,stretch=True)
        sc=ttk.Scrollbar(upper,command=self.tree.yview)
        self.tree.configure(yscrollcommand=sc.set)
        sc.pack(side='right',fill='y')
        self.tree.pack(fill='both',expand=True)
        self.tree.bind('<<TreeviewSelect>>',self._choose_group)
        self._txt(lower,'FILE-BY-FILE DECISIONS   /   FINAL RESULT',9,True,MUTED,bg='#F7FAFB').pack(anchor='w',padx=11,pady=(10,7))
        detailwrap=self._frame(lower,bg='#F7FAFB')
        detailwrap.pack(fill='both',expand=True)
        self.detail=tk.Text(detailwrap,wrap='word',font=('Consolas',10),borderwidth=0,background='#F7FAFB',
                            foreground=INK,padx=13,pady=5,height=7,insertbackground=NAVY)
        detailbar=ttk.Scrollbar(detailwrap,command=self.detail.yview)
        self.detail.configure(yscrollcommand=detailbar.set,state='disabled')
        detailbar.pack(side='right',fill='y')
        self.detail.pack(fill='both',expand=True)
        self.detail.tag_configure('backup',foreground=BAD,font=('Consolas',10,'bold'))
        self.detail.tag_configure('rename',foreground='#A26A16',font=('Consolas',10,'bold'))
        self.detail.tag_configure('keep',foreground='#067E6D',font=('Consolas',10,'bold'))
        self.detail.tag_configure('heading',foreground=NAVY,font=('Consolas',10,'bold'))

        footer=self._frame(self)
        footer.pack(side='bottom', fill='x', before=main)
        bar=self._frame(footer)
        bar.pack(fill='x',padx=26,pady=(9,4))
        self.scan_btn=self._btn(bar,'Scan & preview',self._start_scan,primary=True)
        self.scan_btn.pack(side='left')
        self.export_btn=self._btn(bar,'Export report',self._export)
        self.export_btn.pack(side='left',padx=9)
        self.open_btn=self._btn(bar,'Open folder',self._open_folder)
        self.open_btn.pack(side='left')
        self.backup_btn=self._btn(bar,'Open last backup',self._open_backup)
        self.backup_btn.pack(side='left',padx=9)
        self.apply_btn=self._btn(bar,'Apply cleanup',self._confirm_apply,danger=True)
        self.apply_btn.pack(side='right')
        status=self._frame(footer)
        status.pack(fill='x',padx=26,pady=(0,8))
        self.progress=ttk.Progressbar(status,mode='indeterminate',length=115,style='DPC.Horizontal.TProgressbar')
        self.progress.pack(side='left',padx=(0,11))
        self.status_label=self._txt(status,'',9,color=MUTED,textvariable=self.status_var)
        self.status_label.pack(side='left')
        self._txt(status,'PREVIEW FIRST  ·  BACKUP ALWAYS  ·  NO PERMANENT DELETE',8,True,TEAL).pack(side='right')

    def _preset_changed(self,event=None):
        label=self.preset_var.get()
        for name,ext_main,ext_side in PRESETS:
            if name == label and ext_main:
                self.main_var.set(ext_main)
                self.sidecar_var.set(ext_side)
                return

    def _browse(self):
        path=filedialog.askdirectory(parent=self,title='Choose a folder to scan',mustexist=True,
                                     initialdir=self.folder_var.get() if Path(self.folder_var.get()).is_dir() else None)
        if path: self.folder_var.set(path)

    def _invalidate(self):
        if self._busy: return
        if self._result is not None:
            self._result=None
            self._selected_group=None
            self._row_groups={}
            for item in self.tree.get_children(): self.tree.delete(item)
            self._set_detail('Settings changed. Scan again to review a fresh plan.')
            for val in self.stat_vars.values(): val.set('0')
            self.status_var.set('Settings changed — scan again before applying.')
            self.apply_btn.configure(state='disabled')
            self.export_btn.configure(state='disabled')

    def _mark_idle(self):
        self._set_detail('Select a folder, choose your main and companion extensions, then click Scan & preview.\n\nNo files are changed during a scan.')
        self.apply_btn.configure(state='disabled')
        self.export_btn.configure(state='disabled')
        self.backup_btn.configure(state='disabled')
        self.progress.pack_forget()

    def _set_detail(self,value):
        self.detail.configure(state='normal')
        self.detail.delete('1.0','end')
        self.detail.insert('end',value)
        self.detail.configure(state='disabled')

    def _busy_mode(self,is_busy,apply=False):
        self._busy=is_busy
        self._applying=is_busy and apply
        state='disabled' if is_busy else 'normal'
        for widget in (self.folder_entry,self.main_entry,self.side_entry,self.browse_btn,
                       self.preset_combo,self.recursive_chk,self.scan_btn):
            widget.configure(state=state if widget != self.preset_combo else ('disabled' if is_busy else 'readonly'))
        self.apply_btn.configure(state='disabled' if is_busy else ('normal' if self._result and self._result.changes else 'disabled'))
        self.export_btn.configure(state='disabled' if is_busy or self._result is None else 'normal')
        if is_busy:
            self.progress.pack(side='left',padx=(0,11),before=self.status_label) if not self.progress.winfo_manager() else None
            self.progress.start(12)
        else:
            self.progress.stop()
            self.progress.pack_forget()

    def _start_scan(self):
        if self._busy: return
        folder=self.folder_var.get().strip().strip('"')
        m=self.main_var.get()
        s=self.sidecar_var.get()
        recursive=self.recursive_var.get()
        # Validate in UI thread before initiating the worker.
        try:
            from file_pair_cleaner import PairType
            PairType(m,s)
            if not Path(folder).expanduser().is_dir():
                raise ValueError('Select an existing folder first.')
        except ValueError as ex:
            messagebox.showerror('Check your selection',str(ex),parent=self)
            return
        self._result=None
        self._last_backup=None
        self.backup_btn.configure(state='disabled')
        self.status_var.set('Scanning filenames. Nothing will be modified…')
        self._busy_mode(True)
        def worker():
            try:
                result=scan(folder,m,s,recursive)
                self._events.put(('scan_ok',result))
            except Exception as ex:
                self._events.put(('error',('Scan failed',str(ex))))
        threading.Thread(target=worker,daemon=True).start()

    def _drain_events(self):
        try:
            while True:
                kind,payload=self._events.get_nowait()
                if kind=='scan_ok':
                    self._result=payload
                    self._busy_mode(False)
                    for key,n in [('groups',len(payload.groups)),('backups',payload.backups),
                                  ('renames',payload.renames),('warnings',len(payload.warnings))]:
                        self.stat_vars[key].set(str(n))
                    self._populate_groups()
                    self.status_var.set(f'Preview ready  •  {len(payload.groups)} groups  •  {len(payload.warnings)} warnings  •  no files modified')
                    if payload.warnings:
                        messagebox.showwarning('Some groups were skipped',
                            f'{len(payload.warnings)} group(s) need attention and were excluded from changes.\n\n'+
                            '\n'.join(payload.warnings[:5])+ ('\n…' if len(payload.warnings)>5 else ''),parent=self)
                elif kind=='apply_ok':
                    self._busy_mode(False)
                    self._last_backup=payload
                    self.backup_btn.configure(state='normal' if payload else 'disabled')
                    self.status_var.set('Cleanup completed successfully. Backup retained.')
                    self._result=None
                    self.apply_btn.configure(state='disabled')
                    self.export_btn.configure(state='disabled')
                    messagebox.showinfo('Cleanup complete',
                        'All selected changes were applied.\n\nBackup folder:\n'+str(payload),parent=self)
                elif kind=='error':
                    self._busy_mode(False)
                    self.status_var.set(payload[0]+': '+payload[1])
                    messagebox.showerror(payload[0],payload[1]+'\n\nReview the folder and any backups before retrying.',parent=self)
        except queue.Empty:
            pass
        if self.winfo_exists(): self.after(90,self._drain_events)

    def _populate_groups(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        self._row_groups={}
        self._selected_group=None
        self._set_detail('Select any group in the list to see the exact file decisions.')
        if self._result is None: return
        for idx,group in enumerate(self._result.filter_groups(self.query_var.get(),self.filter_var.get()),1):
            item=self.tree.insert('', 'end', text=(str(group.main.path.parent.relative_to(self._result.folder)) + ' / ' if group.main.path.parent != self._result.folder else '') + group.title,
                    values=('YES' if group.sidecar else 'NO',len(group.changes),group.reason))
            self._row_groups[item]=group
        if self._row_groups:
            first=next(iter(self._row_groups))
            self.tree.selection_set(first)
            self.tree.focus(first)
            self._choose_group()
        elif self._result.warnings:
            self._set_detail('No matching groups for this filter.\nWarnings:\n'+'\n'.join(self._result.warnings))

    def _choose_group(self,event=None):
        selected=self.tree.selection()
        if not selected or self._result is None: return
        group=self._row_groups.get(selected[0])
        if group is None: return
        self._selected_group=group
        change_for={ch.source:ch for ch in group.changes}
        lines=[f'{group.title}',group.reason,'', 'CURRENT FILES / DECISIONS']
        for item in group.items:
            change=change_for.get(item.path)
            if change is None: lines.append('[KEEP]    '+item.path.name)
            elif change.action == 'backup': lines.append('[BACKUP]  '+item.path.name)
            else:
                lines.append('[RENAME]  '+item.path.name)
                lines.append('       -> '+change.target.name)
        lines.extend(['','FINAL RESULT',group.final_main.name,
                      group.final_sidecar.name if group.final_sidecar else '(no companion available)'])
        self.detail.configure(state='normal')
        self.detail.delete('1.0','end')
        for line in lines:
            tag=('backup' if line.startswith('[BACKUP]') else
                 'rename' if line.startswith('[RENAME]') else
                 'keep' if line.startswith('[KEEP]') else
                 'heading' if line in ('CURRENT FILES / DECISIONS','FINAL RESULT') else None)
            self.detail.insert('end',line+'\n',tag)
        self.detail.configure(state='disabled')

    def _export(self):
        if not self._result: return
        path=filedialog.asksaveasfilename(parent=self,title='Save complete preview',defaultextension='.txt',
                                          filetypes=[('Text report','*.txt')],initialfile='Duplicate_Pair_Cleaner_Preview.txt')
        if not path: return
        try:
            Path(path).write_text(self._result.report(),encoding='utf-8-sig')
        except OSError as ex:
            messagebox.showerror('Cannot save report',str(ex),parent=self)
            return
        self.status_var.set('Complete preview exported to '+path)

    def _confirm_apply(self):
        if self._busy or not self._result or not self._result.changes: return
        r=self._result
        msg=(f'You are about to clean {len(r.groups)} groups.\n\n'
             f'Files moved to a dated backup: {r.backups}\n'
             f'Files renamed: {r.renames}\n\n'
             f'Selected folder:\n{r.folder}\n\n'
             'Backups are retained. This action does NOT permanently delete files.\n'
             'Have you reviewed the proposed changes?')
        if not messagebox.askyesno('Confirm cleanup — review carefully',msg,icon='warning',parent=self): return
        self._busy_mode(True,apply=True)
        self.status_var.set('Applying changes with backup and rollback protection. Please wait…')
        # UI stays responsive; closing is prevented until the transaction finishes.
        def worker():
            try: self._events.put(('apply_ok',r.apply()))
            except BaseException as ex: self._events.put(('error',('Cleanup was not completed',str(ex))))
        threading.Thread(target=worker,daemon=True).start()

    def _open_folder(self):
        path=self.folder_var.get().strip()
        if path and Path(path).is_dir():
            try: open_in_file_manager(Path(path))
            except OSError as ex: messagebox.showerror('Cannot open folder',str(ex),parent=self)

    def _open_backup(self):
        if self._last_backup and self._last_backup.is_dir():
            try: open_in_file_manager(self._last_backup)
            except OSError as ex: messagebox.showerror('Cannot open backup',str(ex),parent=self)

    def _on_close(self):
        if self._applying:
            messagebox.showwarning('Cleanup in progress',
                'Please wait for the current file operation to finish before closing.',parent=self)
            return
        if self._busy and not messagebox.askyesno('Scanning in progress',
                 'A background scan is running. No files have been changed. Close anyway?',parent=self):
            return
        self.destroy()


def main():
    root=MainWindow()
    root.mainloop()


if __name__ == '__main__':
    main()
