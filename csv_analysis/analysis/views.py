import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from django.shortcuts import render
from django.http import HttpResponse
from .models import UploadFileForm
import base64
from pandas.errors import ParserError
# Create your views here.

def handle_uploaded_file(f):
    try:
        df=pd.read_csv(f)
    except ParserError as e:
        return None,str(e)
    return df,None

def upload_file(request):
    form=UploadFileForm()

    if request.method =='POST':
        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            df,error=handle_uploaded_file(request.FILES['file'])
            if error:
                return render(request,'analysis/upload.html',{'form':form,'error':error})

            summary={
                'head':df.head().to_html(),
                'describe':df.describe().to_html(),
                'missing_values':df.isna().sum().to_frame().to_html()

            }
            plots=[]
            for column in df.select_dtypes(include=['number']).columns:
                plt.figure()
                sns.histplot(df[column],kde=True)
                plt.title(f"Histogram of {column}")
                plt.xlabel(column)
                plt.ylabel("Frequency")
                buffer=BytesIO()
                plt.savefig(buffer,format='png')
                buffer.seek(0)
                image_base64=base64.b64encode(buffer.getvalue()).decode('utf-8')
                plots.append(image_base64)
                plt.close()
           
            context={
                'form':form,
                'summary':summary,
                'plots':plots
            }
            return render(request,'analysis/upload.html',context)
    return render(request,'analysis/upload.html',{'form':form})
