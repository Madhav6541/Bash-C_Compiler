from flask import Flask, render_template, request
from lex import *
from emit import *
from parse import *
import os
import subprocess

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compile', methods=['POST'])
def compile():
    file = request.files['file']
    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    print(os.listdir(UPLOAD_FOLDER)) # <-- add this line to check the contents of the uploads directory
    with open(os.path.join(UPLOAD_FOLDER, file.filename), 'r') as inputFile:
        source = inputFile.read()

    # Initialize the lexer, emitter, and parser.
    lexer = Lexer(source)
    emitter = Emitter("out.c")
    parser = Parser(lexer, emitter)

    parser.program() # Start the parser.
    emitter.writeFile() # Write the output to file.
    
    with open("out.c", 'r') as outputFile:
        output = outputFile.read()

    return render_template('index.html', output=output)

@app.route('/run', methods=['POST'])
def run_code():
    input_data = request.form['input']
    with open("out.c", 'r') as inputFile:
        source = inputFile.read()

    # Compile the C code.
    compile_result = subprocess.run(['gcc', '-o', 'out.exe', 'out.c'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if compile_result.returncode != 0:
        result = compile_result.stderr.decode()
    else:
        # Run the compiled program.
        run_result = subprocess.run('./out', input=input_data.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = run_result.stdout.decode()

    return render_template('index.html', output=request.form['output'], result=result)

if __name__ == '__main__':
    app.run(debug=True)
