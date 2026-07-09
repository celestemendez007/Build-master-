import os
from flask import Flask, send_from_directory, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='.')

HTML_FILE = 'index.html'
# Permitir subida de pdfs, docs, imagenes
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'pdf', 'doc', 'docx', 'odt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

EDITOR_JS = """
// Script inyectado para edición visual
let isEditing = false;
let currentTargetForUpload = null; // Guardar a quién se le asignará el archivo

// Input invisible para archivos
const fileInput = document.createElement('input');
fileInput.type = 'file';
fileInput.id = 'wysiwyg-file-upload';
fileInput.style.display = 'none';
document.body.appendChild(fileInput);

// Al elegir archivo, subir al servidor y actualizar DOM
fileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if(!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const res = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        
        if (data.status === 'success') {
            const filename = data.filename;
            // Actualizar el DOM dependiendo de qué clickeamos
            if (currentTargetForUpload.tagName.toLowerCase() === 'img') {
                currentTargetForUpload.src = filename;
            } else if (currentTargetForUpload.tagName.toLowerCase() === 'a') {
                currentTargetForUpload.href = filename;
            }
            alert(`Archivo actualizado correctamente: ${filename}`);
        } else {
            alert('Error al subir: ' + data.message);
        }
    } catch (err) {
        alert('Error de red al subir archivo.');
    }
    // Limpiar input
    fileInput.value = '';
});


// Crear el botón flotante
const btnContainer = document.createElement('div');
btnContainer.id = 'wysiwyg-editor-toolbar';
btnContainer.style.position = 'fixed';
btnContainer.style.bottom = '20px';
btnContainer.style.right = '20px';
btnContainer.style.zIndex = '999999';
btnContainer.style.display = 'flex';
btnContainer.style.gap = '10px';
btnContainer.style.background = '#1450AA';
btnContainer.style.padding = '10px 15px';
btnContainer.style.borderRadius = '50px';
btnContainer.style.boxShadow = '0 10px 25px rgba(0,0,0,0.3)';

const toggleBtn = document.createElement('button');
toggleBtn.innerHTML = '✏️ Habilitar Edición';
toggleBtn.style.padding = '10px 20px';
toggleBtn.style.border = 'none';
toggleBtn.style.borderRadius = '25px';
toggleBtn.style.background = '#fff';
toggleBtn.style.color = '#1450AA';
toggleBtn.style.fontWeight = 'bold';
toggleBtn.style.cursor = 'pointer';

const saveBtn = document.createElement('button');
saveBtn.innerHTML = '💾 Guardar Cambios';
saveBtn.style.padding = '10px 20px';
saveBtn.style.border = 'none';
saveBtn.style.borderRadius = '25px';
saveBtn.style.background = '#F8FE12';
saveBtn.style.color = '#000';
saveBtn.style.fontWeight = 'bold';
saveBtn.style.cursor = 'pointer';
saveBtn.style.display = 'none'; // Hidden initially

btnContainer.appendChild(toggleBtn);
btnContainer.appendChild(saveBtn);
document.body.appendChild(btnContainer);

// Elementos editables de texto
const editableTags = 'h1, h2, h3, h4, p, td, span';

// Handlers de imágenes y enlaces
function handleImageClick(e) {
    if(!isEditing) return;
    e.preventDefault();
    currentTargetForUpload = e.currentTarget;
    fileInput.accept = 'image/*';
    fileInput.click();
}

function handleLinkDblClick(e) {
    if(!isEditing) return;
    e.preventDefault();
    currentTargetForUpload = e.currentTarget;
    fileInput.accept = '.pdf,.doc,.docx,.odt';
    fileInput.click();
}

toggleBtn.addEventListener('click', () => {
    isEditing = !isEditing;
    const textElements = document.querySelectorAll(editableTags);
    const images = document.querySelectorAll('img');
    const links = document.querySelectorAll('a');
    
    if (isEditing) {
        toggleBtn.innerHTML = '❌ Cancelar Edición';
        saveBtn.style.display = 'block';
        
        // Textos editables
        textElements.forEach(el => {
            if(el.closest('#wysiwyg-editor-toolbar')) return;
            el.setAttribute('contenteditable', 'true');
            el.style.outline = '2px dashed rgba(248, 254, 18, 0.5)';
            el.style.outlineOffset = '2px';
            el.addEventListener('focus', function() {
                this.style.outline = '2px solid #F8FE12';
                this.style.backgroundColor = 'rgba(255,255,255,0.1)';
            });
            el.addEventListener('blur', function() {
                this.style.outline = '2px dashed rgba(248, 254, 18, 0.5)';
                this.style.backgroundColor = 'transparent';
            });
        });
        
        // Imágenes (Clic normal sube archivo)
        images.forEach(img => {
            img.style.cursor = 'pointer';
            img.style.outline = '2px dashed #00c3ff';
            img.title = 'Clic para cambiar imagen';
            img.addEventListener('click', handleImageClick);
        });
        
        // Enlaces (Doble clic sube archivo)
        links.forEach(a => {
            a.title = 'Doble clic para cambiar archivo enlazado';
            a.addEventListener('dblclick', handleLinkDblClick);
            
            // También permitir editar texto del enlace
            if (!a.querySelector('img')) {
                a.setAttribute('contenteditable', 'true');
            }
        });

    } else {
        if(confirm('¿Seguro que quieres cancelar? Los cambios no guardados se perderán.')){
            window.location.reload();
        }
    }
});

saveBtn.addEventListener('click', () => {
    // 1. Quitar el contenteditable, outlines y listeners
    const textElements = document.querySelectorAll(editableTags);
    textElements.forEach(el => {
        el.removeAttribute('contenteditable');
        el.style.outline = '';
        el.style.outlineOffset = '';
        el.style.backgroundColor = '';
    });
    
    document.querySelectorAll('img').forEach(img => {
        img.style.cursor = '';
        img.style.outline = '';
        img.removeAttribute('title');
        img.removeEventListener('click', handleImageClick);
    });
    
    document.querySelectorAll('a').forEach(a => {
        a.removeAttribute('title');
        a.removeAttribute('contenteditable');
        a.removeEventListener('dblclick', handleLinkDblClick);
    });
    
    // 2. Obtener el HTML
    const clonedHtml = document.documentElement.cloneNode(true);
    
    // 3. Remover componentes del editor
    const toolbar = clonedHtml.querySelector('#wysiwyg-editor-toolbar');
    if (toolbar) toolbar.remove();
    
    const input = clonedHtml.querySelector('#wysiwyg-file-upload');
    if (input) input.remove();
    
    const injectedScript = clonedHtml.querySelector('#injected-editor-script');
    if (injectedScript) injectedScript.remove();
    
    const finalHtml = '<!DOCTYPE html>\\n<html lang="es">\\n' + clonedHtml.innerHTML + '\\n</html>';
    
    // 4. Enviar
    saveBtn.innerHTML = 'Guardando...';
    fetch('/api/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ html: finalHtml })
    })
    .then(res => res.json())
    .then(data => {
        if(data.status === 'success') {
            alert('¡Sitio guardado exitosamente!');
            window.location.reload();
        } else {
            alert('Error al guardar: ' + data.message);
            saveBtn.innerHTML = '💾 Guardar Cambios';
        }
    })
    .catch(err => {
        alert('Error de red al guardar.');
        saveBtn.innerHTML = '💾 Guardar Cambios';
    });
});
"""

@app.route('/admin')
def admin_page():
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    injection = '<script id="injected-editor-script" src="/editor.js"></script></body>'
    if '</body>' in html_content:
        html_content = html_content.replace('</body>', injection)
    else:
        html_content += injection.replace('</body>', '')
        
    return html_content

@app.route('/editor.js')
def serve_editor_js():
    return EDITOR_JS, 200, {'Content-Type': 'application/javascript'}

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Guardar en la misma carpeta del proyecto para referencias relativas
        file.save(os.path.join('.', filename))
        return jsonify({'status': 'success', 'filename': filename})
    else:
        return jsonify({'status': 'error', 'message': 'File type not allowed'}), 400

@app.route('/api/save', methods=['POST'])
def save_html():
    try:
        data = request.json
        new_html = data.get('html')
        if not new_html:
            return jsonify({'status': 'error', 'message': 'No HTML provided'}), 400
            
        with open(HTML_FILE, 'w', encoding='utf-8') as f:
            f.write(new_html)
            
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    print("\n=========================================")
    print(" MODO EDICION VISUAL AVANZADO ")
    print("Abre tu navegador en: http://127.0.0.1:5000/admin")
    print("=========================================\n")
    app.run(debug=True, port=5000)
