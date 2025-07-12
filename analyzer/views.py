from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
import pandas as pd
import sqlite3
from tempfile import NamedTemporaryFile

class FileUploadAPIView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, format=None):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': 'No file uploaded'}, status=400)

        filename = file_obj.name
        ext = filename.split('.')[-1].lower()

        try:
            if ext == 'csv':
                df = pd.read_csv(file_obj)
            elif ext in ['xls', 'xlsx']:
                df = pd.read_excel(file_obj)
            elif ext == 'sqlite':
                with NamedTemporaryFile(delete=False) as temp:
                    for chunk in file_obj.chunks():
                        temp.write(chunk)
                    conn = sqlite3.connect(temp.name)
                    table = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchone()[0]
                    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
                    conn.close()
            else:
                return Response({'error': 'Unsupported file type'}, status=400)

            # Save in session or return directly
            request.session['df'] = df.to_json()
            preview = df.head(10).to_dict(orient='records')
            return Response({'columns': list(df.columns), 'preview': preview}, status=200)

        except Exception as e:
            return Response({'error': str(e)}, status=500)
