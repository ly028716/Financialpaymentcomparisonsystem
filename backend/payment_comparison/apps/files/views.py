"""
文件管理视图
"""
import os
import uuid
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.conf import settings

from payment_comparison.common.response import ApiResponse


class FileUploadView(APIView):
    """文件上传"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    # 允许的文件类型
    ALLOWED_EXTENSIONS = {
        'image': ['jpg', 'jpeg', 'png', 'gif', 'bmp'],
        'document': ['pdf', 'doc', 'docx', 'xls', 'xlsx'],
    }

    # 文件大小限制（MB）
    MAX_FILE_SIZE = 10

    def post(self, request):
        if 'file' not in request.FILES:
            return ApiResponse.error(400, '请选择要上传的文件')

        upload_file = request.FILES['file']
        file_type = request.data.get('type', 'document')

        # 校验文件大小
        if upload_file.size > self.MAX_FILE_SIZE * 1024 * 1024:
            return ApiResponse.error(400, f'文件大小不能超过{self.MAX_FILE_SIZE}MB')

        # 校验文件类型
        ext = upload_file.name.split('.')[-1].lower()
        allowed_extensions = self.ALLOWED_EXTENSIONS.get(file_type, [])
        if allowed_extensions and ext not in allowed_extensions:
            return ApiResponse.error(
                400,
                f'不支持的文件类型，允许的类型: {", ".join(allowed_extensions)}'
            )

        # 生成文件ID和存储路径
        file_id = f"f_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}"
        file_name = upload_file.name
        today = datetime.now().strftime('%Y/%m/%d')
        file_path = f'uploads/{today}/{file_id}.{ext}'

        # 保存文件
        saved_path = default_storage.save(file_path, upload_file)

        return ApiResponse.success(
            data={
                'file_id': file_id,
                'file_name': file_name,
                'file_url': f'/media/{saved_path}',
                'file_size': upload_file.size,
                'file_type': file_type,
            },
            message='上传成功'
        )


class FileDownloadView(APIView):
    """文件下载"""
    permission_classes = [IsAuthenticated]

    def get(self, request, file_id):
        from django.http import FileResponse, Http404

        # 根据file_id查找文件
        # 这里简化处理，实际应该有文件索引表
        import glob
        patterns = [
            f'uploads/**/{file_id}.*',
        ]

        for pattern in patterns:
            files = glob.glob(os.path.join(settings.MEDIA_ROOT, pattern))
            if files:
                file_path = files[0]
                response = FileResponse(
                    open(file_path, 'rb'),
                    as_attachment=True
                )
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                return response

        return ApiResponse.error(404, '文件不存在')


class FileDeleteView(APIView):
    """文件删除"""
    permission_classes = [IsAuthenticated]

    def delete(self, request, file_id):
        import glob

        patterns = [
            f'uploads/**/{file_id}.*',
        ]

        deleted = False
        for pattern in patterns:
            files = glob.glob(os.path.join(settings.MEDIA_ROOT, pattern))
            for file_path in files:
                os.remove(file_path)
                deleted = True

        if deleted:
            return ApiResponse.success(message='文件删除成功')
        return ApiResponse.error(404, '文件不存在')