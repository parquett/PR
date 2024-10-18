import re


class CustomSerializer:

    def serialize(self, data):
        """Serializes a Python object into a custom format."""
        if isinstance(data, dict):
            # Dictionary serialization
            items = []
            for k, v in data.items():
                serialized_key = f"k:{self._serialize_value(k)}"
                serialized_value = f"v:{self._serialize_value(v)}"
                items.append(f"D:{serialized_key}:{serialized_value}")
            return f"{'; '.join(items)}"
        elif isinstance(data, list):
            # List serialization
            serialized_items = [self.serialize(item) for item in data]
            return f"L:[{'; '.join(serialized_items)}]"
        else:
            # For basic data types
            return self._serialize_value(data)

    def deserialize(self, data_str):
        """Deserializes the custom format string back into a Python object."""
        if data_str.startswith("L:["):
            # Handle list/dictionary
            return self._deserialize_list_or_dict(data_str)
        else:
            # For basic data types
            return self._deserialize_value(data_str)

    def _serialize_value(self, value):
        """Helper function to serialize a basic value."""
        if isinstance(value, int):
            return f"int({value})"
        elif isinstance(value, str):
            return f"str({value})"
        elif isinstance(value, float):
            return f"float({value})"
        elif isinstance(value, bool):
            return f"bool({str(value).lower()})"
        else:
            raise TypeError(f"Unsupported type: {type(value)}")

    def _deserialize_value(self, value_str):
        """Helper function to deserialize a basic value."""
        if value_str.startswith("int("):
            return int(value_str[4:-1])
        elif value_str.startswith("str("):
            return value_str[4:-1]
        elif value_str.startswith("float("):
            return float(value_str[6:-1])
        elif value_str.startswith("bool("):
            return value_str[5:-1] == "true"
        else:
            raise TypeError(f"Unsupported serialized type: {value_str}")

    def _deserialize_list_or_dict(self, list_str):
        """Helper function to deserialize a list or list of dictionaries."""
        list_str = list_str[3:-1]  # Remove L:[ and final ]
        items = self._split_items(list_str)
        result = []
        for item in items:
            if item.startswith("D:"):
                # It's a dictionary item
                result.append(self._deserialize_dict(item))
            else:
                # It's a regular list item
                result.append(self.deserialize(item))
        return result

    def _deserialize_dict(self, dict_str):
        """Helper function to deserialize a dictionary."""
        dict_str = dict_str[2:]  # Remove 'D:' prefix
        key_match = re.search(r"k:(\w+?)\((.+?)\):v:(\w+?)\((.+?)\)", dict_str)
        if key_match:
            key_type, key_value, value_type, value_value = key_match.groups()
            key = self._deserialize_value(f"{key_type}({key_value})")
            value = self._deserialize_value(f"{value_type}({value_value})")
            return {key: value}
        else:
            raise ValueError("Failed to parse dictionary from serialized format")

    def _split_items(self, s):
        """Helper function to split serialized list items, handling nested structures."""
        items = []
        stack = []
        current = []
        for char in s:
            if char == '[':
                stack.append(char)
            elif char == ']':
                stack.pop()
            if char == ';' and not stack:
                items.append(''.join(current).strip())
                current = []
            else:
                current.append(char)
        if current:
            items.append(''.join(current).strip())
        return items


serializer = CustomSerializer()

data = [{"key1": "val1"}, {"key2": 2}]
serialized_data = serializer.serialize(data)
print("Serialized:", serialized_data)

deserialized_data = serializer.deserialize(serialized_data)
print("Deserialized:", deserialized_data)
