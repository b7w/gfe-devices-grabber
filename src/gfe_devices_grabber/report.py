from openpyxl import Workbook


def create_report(records, fname):
    wb = Workbook()
    ws = wb.active
    for lt in 'CDEF':
        ws.column_dimensions[lt].width = 32
    ws.append(['Loop', 'Device', 'Device Text', 'Type', 'Zone', 'Comments', 'Value'])
    for row in records:
        ws.append([i.strip() for i in row])
    wb.save(fname)
