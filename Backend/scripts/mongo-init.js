// MongoDB initialization script for DataWise Dashboard
// This script runs when MongoDB container starts for the first time

// Switch to the datawiser_sessions database
db = db.getSiblingDB('datawiser_sessions');

// Create collections with proper indexes
db.createCollection('sessions');
db.createCollection('query_cache');
db.createCollection('rate_limits');
db.createCollection('user_activity_logs');
db.createCollection('vector_embeddings');
db.createCollection('request_latency');

// Create indexes for better performance
db.sessions.createIndex({ "user_id": 1 });
db.sessions.createIndex({ "expires_at": 1 }, { expireAfterSeconds: 0 });
db.sessions.createIndex({ "session_id": 1 }, { unique: true });

db.query_cache.createIndex({ "query_hash": 1 });
db.query_cache.createIndex({ "tenant_id": 1 });
db.query_cache.createIndex({ "created_at": 1 }, { expireAfterSeconds: 86400 }); // 24 hours TTL

db.rate_limits.createIndex({ "user_id": 1, "endpoint": 1 });
db.rate_limits.createIndex({ "expires_at": 1 }, { expireAfterSeconds: 0 });

db.user_activity_logs.createIndex({ "user_id": 1 });
db.user_activity_logs.createIndex({ "timestamp": 1 });
db.user_activity_logs.createIndex({ "action": 1 });

db.vector_embeddings.createIndex({ "tenant_id": 1 });
db.vector_embeddings.createIndex({ "embedding_type": 1 }); // schema, query, etc.

// Request latency indexes for performance monitoring
db.request_latency.createIndex({ "user_id": 1 });
db.request_latency.createIndex({ "endpoint": 1 });
db.request_latency.createIndex({ "tenant_id": 1 });
db.request_latency.createIndex({ "timestamp": 1 });
db.request_latency.createIndex({ "hour": 1 });
db.request_latency.createIndex({ "status_code": 1 });
db.request_latency.createIndex({ "latency_ms": 1 });
db.request_latency.createIndex({ "timestamp": 1 }, { expireAfterSeconds: 2592000 }); // 30 days TTL

// Create a user for the application
db.createUser({
  user: "datawiser_app",
  pwd: "datawiser_app_password",
  roles: [
    { role: "readWrite", db: "datawiser_sessions" }
  ]
});

print("MongoDB initialization completed successfully!");
print("Created collections: sessions, query_cache, rate_limits, user_activity_logs, vector_embeddings, request_latency"); 