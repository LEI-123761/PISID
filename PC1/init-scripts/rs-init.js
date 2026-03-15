// rs-init.js
print("Waiting 5s for MongoDB to start...");
sleep(5000); // wait for mongo1

print("Initializing replica set...");
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "mongo1:27017", priority: 2 },
    { _id: 1, host: "mongo2:27017", priority: 1 },
    { _id: 2, host: "mongo3:27017", priority: 1 }
  ]
});

print("Creating dummy collection to avoid GUI warnings...");
db = db.getSiblingDB("config");
db.image_collection.insertOne({ initialized: true });

print("Replica set initialized!");