@if not exist generated_proto mkdir generated_proto
protoc --proto_path=. --proto_path=C:\protobuf-2.5.0\src --python_out=generated_proto netmessages_public.proto
protoc --proto_path=. --proto_path=C:\protobuf-2.5.0\src --python_out=generated_proto cstrike15_usermessages_public.proto