#!/usr/bin/python3
from flask import Flask, render_template, request, send_from_directory, make_response
import os
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

class UniqueInt:
    def __init__(self):
        self.seen = [False] * 2047
        self.min_int = -1023

    def process_file(self, input_file_path):
        self.seen = [False] * 2047
        unique_numbers = self.read_unique_integers(input_file_path)
        return unique_numbers

    def read_unique_integers(self, input_file_path):
        unique_numbers = []
        with open(input_file_path, 'r') as input_file:
            for line in input_file:
                stripped_line = line.strip()
                if stripped_line:
                    if self.is_valid_integer_line(stripped_line):
                        number = int(stripped_line)
                        if -1023 <= number <= 1023:
                            if not self.seen[number - self.min_int]:
                                self.seen[number - self.min_int] = True
                                unique_numbers.append(number)
                        else:
                            print(f"Number out of range: {number}")
        return self.sort_unique_numbers(unique_numbers)

    def is_valid_integer_line(self, line):
        try:
            int(line)
            return True
        except ValueError:
            print(f"Invalid integer line: {line}")
            return False

    def sort_unique_numbers(self, numbers):
        if not numbers:
            return numbers

        n = len(numbers)
        for i in range(n):
            for j in range(0, n-i-1):
                if numbers[j] > numbers[j+1]:
                    numbers[j], numbers[j+1] = numbers[j+1], numbers[j]
        return numbers

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        return 'No file part'
    files = request.files.getlist('files')
    if len(files) == 0:
        return 'No selected files'
    processing_results = []
    for file in files:
        if file.filename == '':
            continue
        if file:
            unique_int_processor = UniqueInt()
            filename = file.filename
            input_path = os.path.join('./uploads', filename)
            output_path = os.path.join('./results', f"{filename}_processed.txt")
            file.save(input_path)
            start_time = time.time()
            unique_numbers = unique_int_processor.process_file(input_path)
            end_time = time.time()
            with open(output_path, 'w') as output_file:
                for number in unique_numbers:
                    output_file.write(f"{number}\n")
            processing_info = f"Processed {filename} in {end_time - start_time:.4f} seconds. <a href='/download/{filename}_processed.txt'>Download processed file</a>"
            processing_results.append(processing_info)
    return render_template('result.html', processing_results=processing_results)

@app.route('/download/<filename>')
def download_file(filename):
    response = make_response(send_from_directory('./results', filename))
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response

if __name__ == "__main__":
    app.run(debug=True)

