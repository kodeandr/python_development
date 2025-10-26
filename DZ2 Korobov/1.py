with open('source.txt', 'r', encoding='utf-8') as src_file:
    content = src_file.read()
with open('destination.txt', 'w', encoding='utf-8') as dest_file:
    dest_file.write(content)

print('Файл успешно скопирован!')