from django.contrib import admin

from .models import Follow, Comment, Post, Group


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    search_fields = ('text',)
    list_filter = ('pub_date', 'group',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)


class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    search_fields = ('title',)
    list_filter = ('title',)
    prepopulated_fields = {"slug": ("title",)}
    empty_value_display = '-пусто-'


admin.site.register(Group, GroupAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'author', 'post_id', 'created')
    search_fields = ('text',
                     'author__username',
                     'author__first_name',
                     'author__last_name')
    list_filter = ('created', 'author',)
    empty_value_display = '-пусто-'

    def post_id(self, obj):
        return obj.post.id

    post_id.short_description = 'ID поста'


admin.site.register(Comment, CommentAdmin)


class FollowAdmin(admin.ModelAdmin):
    search_fields = ('author__username',
                     'author__first_name',
                     'author__last_name',
                     'user__username',
                     'user__first_name',
                     'user__last_name')


admin.site.register(Follow, FollowAdmin)
