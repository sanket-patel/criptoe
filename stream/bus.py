import redis
import redispy
import webclient

# takes messages in from webclient and drops into redis client

class bus(redis.StrictRedis):
    def process_stream(sock):
        
