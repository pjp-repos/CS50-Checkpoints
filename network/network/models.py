
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models import Max,Sum,Count


class User(AbstractUser):
    followedUsers = models.ManyToManyField('self', through='Follow',
                                           symmetrical=False,
                                           related_name='followerUsers')

    def add_follow(self, followedUser):
        follow, created = Follow.objects.get_or_create(
            follower=self,
            followed=followedUser)
        return follow

    def remove_follow(self, followedUser):
        Follow.objects.filter(
            follower=self,
            followed=followedUser).delete()
        return

    def get_followedUsers(self):
        return self.followedUsers.all()

    def get_followerUsers(self):
        return self.followerUsers.all()

    def get_followed(self):
        return self.followedUsers.all().count()

    def get_follower(self):
        return self.followerUsers.all().count()

    def get_others(self,user):
        return User.objects.all().exclude(pk=user.pk)

    #   def get_followlist(self):
    #       usersFollowed = self.get_followed.annotate(followed=True)
    #       usersNotFollowed = User.objects.all().exclude(pk=self.pk).exclude(pk__in=usersFollowed.pk).annotate(followed=False)
    #       return usersFollowed | usersNotFollowed

    def serialize(self,user):
        if self in user.followedUsers.all():
            follow = '(Following)'
        else:
            follow = ''
        return {
            "id": self.id,
            "user": self.username,
            "follow": follow
        }


class Follow(models.Model):
    follower = models.ForeignKey(User,on_delete=CASCADE, related_name='rnFollow_follower')
    followed = models.ForeignKey(User,on_delete=CASCADE, related_name='rnFollow_followed')
   
    class Meta:
        models.UniqueConstraint(fields=['follower', 'followed'], name='uniqueFollow') 

    def __str__(self):
        return f"{self.follower} is following to {self.followed}"


class Post(models.Model):
    user = models.ForeignKey(User,on_delete=CASCADE, related_name="posts")   
    text = models.CharField(max_length=128)
    likes =models.ManyToManyField(User, through='Like',
                                           symmetrical=False,
                                           related_name='liked_posts')
    firstTimeStamp = models.DateTimeField(auto_now_add=True)
    lastTimeStamp = models.DateTimeField(auto_now=True)

    def get_all(self):
        return Post.objects.all().order_by("-firstTimeStamp")

    def get_own(self,user):
        return Post.objects.filter(user=user).order_by("-firstTimeStamp")

    def get_follow(self,user):
        followed = user.get_followedUsers()
        return Post.objects.filter(user__in=followed).order_by("-firstTimeStamp")

    def add_like(self, user):
        like, created = Like.objects.get_or_create(post=self,user=user)
        return like

    def remove_like(self, user):
        Like.objects.filter(post=self, user=user).delete()
        return
    
    def serialize(self,user):
        if user in self.likes.all():
            like = True
        else:
            like = False
        return {
            "id": self.id,
            "user": self.user.username,
            "userId": self.user.id,
            "text": self.text,
            "firstTimeStamp": self.firstTimeStamp.strftime("%b %d %Y, %I:%M %p"),
            "likeCount": self.likes.count(),
            "like": like
        }
    def __str__(self):
        return f"Posted by {self.user.username} at  {self.firstTimeStamp}: {self.text}"


class Like(models.Model):
    user = models.ForeignKey(User,on_delete=CASCADE, related_name="rnLike_user")   
    post = models.ForeignKey(Post,on_delete=CASCADE, related_name="rnLike_post") 
    
    class Meta:
        models.UniqueConstraint(fields=['user', 'post'], name='unique_like') 

    def __str__(self):
        return f"{self.user.username} likes {self.post}"