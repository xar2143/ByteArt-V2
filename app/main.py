import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from pathlib import Path
from codec import PNGBytesCodec


class PNGCodecGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ByteArt-V2")
        self.root.geometry("700x600")
        
        self.random_seed = tk.StringVar()
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.png_file = tk.StringVar()
        self.decode_output = tk.StringVar()
        
        self.setup_ui()
        
    def setup_ui(self):
       
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # encode
        encode_frame = ttk.Frame(notebook)
        notebook.add(encode_frame, text="Encode (File → PNG)")
        self.setup_encode_tab(encode_frame)
        
        # decode
        decode_frame = ttk.Frame(notebook)
        notebook.add(decode_frame, text="Decode (PNG → File)")
        self.setup_decode_tab(decode_frame)
        
        text_frame = ttk.Frame(notebook)
        notebook.add(text_frame, text="Text Mode")
        self.setup_text_tab(text_frame)
        
    def setup_encode_tab(self, parent):
     
        ttk.Label(parent, text="Input File:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(parent, textvariable=self.input_file, width=60).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(parent, text="Browse", command=self.browse_input_file).grid(row=0, column=2, padx=5, pady=5)
     
        ttk.Label(parent, text="Output PNG:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(parent, textvariable=self.output_file, width=60).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(parent, text="Browse", command=self.browse_output_png).grid(row=1, column=2, padx=5, pady=5)
        
        ttk.Label(parent, text="Random Seed (optional):").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(parent, textvariable=self.random_seed, width=20).grid(row=2, column=1, sticky='w', padx=5, pady=5)
   
        ttk.Button(parent, text="Encode File", command=self.encode_file, style='Accent.TButton').grid(row=3, column=1, pady=20)
    
        self.encode_progress = ttk.Progressbar(parent, mode='indeterminate')
        self.encode_progress.grid(row=4, column=0, columnspan=3, sticky='ew', padx=5, pady=5)
        
        self.encode_status = ttk.Label(parent, text="Ready to encode", foreground='green')
        self.encode_status.grid(row=5, column=0, columnspan=3, pady=5)
   
        info_frame = ttk.LabelFrame(parent, text="File Information")
        info_frame.grid(row=6, column=0, columnspan=3, sticky='ew', padx=5, pady=10)
        
        self.file_info = ttk.Label(info_frame, text="No file selected")
        self.file_info.pack(padx=10, pady=10)
        
        parent.grid_columnconfigure(1, weight=1)
        
    def setup_decode_tab(self, parent):
      
        ttk.Label(parent, text="Input PNG:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(parent, textvariable=self.png_file, width=60).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(parent, text="Browse", command=self.browse_png_file).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(parent, text="Output File:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(parent, textvariable=self.decode_output, width=60).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(parent, text="Browse", command=self.browse_decode_output).grid(row=1, column=2, padx=5, pady=5)
        
        ttk.Button(parent, text="Decode File", command=self.decode_file, style='Accent.TButton').grid(row=2, column=1, pady=20)
        
        self.decode_progress = ttk.Progressbar(parent, mode='indeterminate')
        self.decode_progress.grid(row=3, column=0, columnspan=3, sticky='ew', padx=5, pady=5)
        
        self.decode_status = ttk.Label(parent, text="Ready to decode", foreground='green')
        self.decode_status.grid(row=4, column=0, columnspan=3, pady=5)
        
        info_frame = ttk.LabelFrame(parent, text="PNG Information")
        info_frame.grid(row=5, column=0, columnspan=3, sticky='ew', padx=5, pady=10)
        
        self.png_info = ttk.Label(info_frame, text="No PNG file selected")
        self.png_info.pack(padx=10, pady=10)
        
        parent.grid_columnconfigure(1, weight=1)
        
    def setup_text_tab(self, parent):
     
        ttk.Label(parent, text="Text to encode:").pack(anchor='w', padx=5, pady=5)
        self.text_input = scrolledtext.ScrolledText(parent, height=10, width=80)
        self.text_input.pack(fill='both', expand=True, padx=5, pady=5)
       
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(pady=10)
       
        text_png_frame = ttk.Frame(parent)
        text_png_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(text_png_frame, text="Output PNG:").pack(side='left')
        self.text_output_png = tk.StringVar()
        ttk.Entry(text_png_frame, textvariable=self.text_output_png, width=50).pack(side='left', padx=5)
        ttk.Button(text_png_frame, text="Browse", command=self.browse_text_output_png).pack(side='left', padx=5)
      
        ttk.Button(buttons_frame, text="Encode Text", command=self.encode_text).pack(side='left', padx=5)
        
        ttk.Button(buttons_frame, text="Decode Text from PNG", command=self.decode_text).pack(side='left', padx=5)
        
        ttk.Button(buttons_frame, text="Clear Text", command=self.clear_text).pack(side='left', padx=5)

        self.text_status = ttk.Label(parent, text="Ready", foreground='green')
        self.text_status.pack(pady=5)
        
    def browse_input_file(self):
        filename = filedialog.askopenfilename(
            title="Select file to encode",
            filetypes=[("All files", "*.*")]
        )
        if filename:
            self.input_file.set(filename)
            self.update_file_info()
          
            base_name = Path(filename).stem
            self.output_file.set(f"{base_name}_encoded.png")
            
    def browse_output_png(self):
        filename = filedialog.asksaveasfilename(
            title="Save PNG as",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            initialdir=os.path.expanduser("~/Desktop")  # desktop out
        )
        if filename:
            self.output_file.set(filename)
            
    def browse_png_file(self):
        filename = filedialog.askopenfilename(
            title="Select PNG file to decode",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if filename:
            self.png_file.set(filename)
            self.update_png_info()
            
    def browse_decode_output(self):
        filename = filedialog.asksaveasfilename(
            title="Save decoded file as",
            filetypes=[("All files", "*.*")],
            initialdir=os.path.expanduser("~/Desktop")  # desktop out
        )
        if filename:
            self.decode_output.set(filename)
            
    def browse_text_output_png(self):
        filename = filedialog.asksaveasfilename(
            title="Save PNG as",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            initialdir=os.path.expanduser("~/Desktop")  # desktop out
        )
        if filename:
            self.text_output_png.set(filename)
            
    def update_file_info(self):
        if self.input_file.get() and os.path.exists(self.input_file.get()):
            size = os.path.getsize(self.input_file.get())
            size_str = self.format_size(size)
            name = os.path.basename(self.input_file.get())
            self.file_info.config(text=f"File: {name}\nSize: {size_str}")
        else:
            self.file_info.config(text="No file selected")
            
    def update_png_info(self):
        if self.png_file.get() and os.path.exists(self.png_file.get()):
            size = os.path.getsize(self.png_file.get())
            size_str = self.format_size(size)
            name = os.path.basename(self.png_file.get())
            self.png_info.config(text=f"PNG: {name}\nSize: {size_str}")
        else:
            self.png_info.config(text="No PNG file selected")
            
    def format_size(self, size_bytes):
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024
            i += 1
        return f"{size_bytes:.1f} {size_names[i]}"
        
    def encode_file(self):
        if not self.input_file.get():
            messagebox.showerror("Error", "Please select an input file")
            return
        if not self.output_file.get():
            messagebox.showerror("Error", "Please specify output PNG file")
            return
            
        # check permissions
        input_path = self.input_file.get()
        output_path = self.output_file.get()
        
        if not os.access(input_path, os.R_OK):
            messagebox.showerror("Permission Error", f"Cannot read input file: {input_path}")
            return
            
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.access(output_dir, os.W_OK):
            messagebox.showerror("Permission Error", f"Cannot write to directory: {output_dir}")
            return
            
        def encode_thread():
            try:
                self.encode_progress.start()
                self.encode_status.config(text="Encoding...", foreground='blue')
                
                seed = None
                if self.random_seed.get().strip():
                    seed = int(self.random_seed.get())
                
                PNGBytesCodec.encode_file(
                    input_path,
                    output_path,
                    random_seed=seed
                )
                
                self.encode_status.config(text="Encoding completed successfully!", foreground='green')
                messagebox.showinfo("Success", f"File encoded successfully!\nSaved as: {output_path}")
                
            except PermissionError as e:
                error_msg = f"Permission denied: {str(e)}\nTry running as administrator or choose a different location."
                self.encode_status.config(text="Permission Error", foreground='red')
                messagebox.showerror("Permission Error", error_msg)
            except Exception as e:
                self.encode_status.config(text=f"Error: {str(e)}", foreground='red')
                messagebox.showerror("Error", f"Encoding failed: {str(e)}")
            finally:
                self.encode_progress.stop()
                
        threading.Thread(target=encode_thread, daemon=True).start()
        
    def decode_file(self):
        if not self.png_file.get():
            messagebox.showerror("Error", "Please select a PNG file")
            return
        if not self.decode_output.get():
            messagebox.showerror("Error", "Please specify output file")
            return
            
        # check permissions
        png_path = self.png_file.get()
        output_path = self.decode_output.get()
        
        if not os.access(png_path, os.R_OK):
            messagebox.showerror("Permission Error", f"Cannot read PNG file: {png_path}")
            return
            
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.access(output_dir, os.W_OK):
            messagebox.showerror("Permission Error", f"Cannot write to directory: {output_dir}")
            return
            
        def decode_thread():
            try:
                self.decode_progress.start()
                self.decode_status.config(text="Decoding...", foreground='blue')
                
                PNGBytesCodec.decode_to_file(
                    png_path,
                    output_path
                )
                
                self.decode_status.config(text="Decoding completed successfully!", foreground='green')
                messagebox.showinfo("Success", f"File decoded successfully!\nSaved as: {output_path}")
                
            except PermissionError as e:
                error_msg = f"Permission denied: {str(e)}\nTry running as administrator or choose a different location."
                self.decode_status.config(text="Permission Error", foreground='red')
                messagebox.showerror("Permission Error", error_msg)
            except Exception as e:
                self.decode_status.config(text=f"Error: {str(e)}", foreground='red')
                messagebox.showerror("Error", f"Decoding failed: {str(e)}")
            finally:
                self.decode_progress.stop()
                
        threading.Thread(target=decode_thread, daemon=True).start()
        
    def encode_text(self):
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showerror("Error", "Please enter text to encode")
            return
        if not self.text_output_png.get():
            messagebox.showerror("Error", "Please specify output PNG file")
            return
            
      
        output_path = self.text_output_png.get()
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.access(output_dir, os.W_OK):
            messagebox.showerror("Permission Error", f"Cannot write to directory: {output_dir}")
            return
            
        try:
            self.text_status.config(text="Encoding text...", foreground='blue')
            
            seed = None
            if self.random_seed.get().strip():
                seed = int(self.random_seed.get())
            
            PNGBytesCodec.encode_text(
                text,
                output_path,
                random_seed=seed
            )
            
            self.text_status.config(text="Text encoded successfully!", foreground='green')
            messagebox.showinfo("Success", f"Text encoded successfully!\nSaved as: {output_path}")
            
        except PermissionError as e:
            error_msg = f"Permission denied: {str(e)}\nTry running as administrator or choose a different location."
            self.text_status.config(text="Permission Error", foreground='red')
            messagebox.showerror("Permission Error", error_msg)
        except Exception as e:
            self.text_status.config(text=f"Error: {str(e)}", foreground='red')
            messagebox.showerror("Error", f"Text encoding failed: {str(e)}")
            
    def decode_text(self):
        filename = filedialog.askopenfilename(
            title="Select PNG file to decode",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if not filename:
            return
           
        if not os.access(filename, os.R_OK):
            messagebox.showerror("Permission Error", f"Cannot read PNG file: {filename}")
            return
            
        try:
            self.text_status.config(text="Decoding text...", foreground='blue')
            
            decoded_text = PNGBytesCodec.decode_text(filename)
            
            self.text_input.delete("1.0", tk.END)
            self.text_input.insert("1.0", decoded_text)
            
            self.text_status.config(text="Text decoded successfully!", foreground='green')
            
        except PermissionError as e:
            error_msg = f"Permission denied: {str(e)}\nTry running as administrator."
            self.text_status.config(text="Permission Error", foreground='red')
            messagebox.showerror("Permission Error", error_msg)
        except Exception as e:
            self.text_status.config(text=f"Error: {str(e)}", foreground='red')
            messagebox.showerror("Error", f"Text decoding failed: {str(e)}")
            
    def clear_text(self):
        self.text_input.delete("1.0", tk.END)
        self.text_status.config(text="Text cleared", foreground='green')


def main():
    root = tk.Tk()
    app = PNGCodecGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
