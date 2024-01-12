from hashids import Hashids

hashids = Hashids(
        salt="jS5qAlR0kHbAeqeuVowPBnyotKuTvvlGzIzkEtz79XQGB7BJHb",
        min_length=8,
        alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    )

def hash_id(id: int) -> str:
    return hashids.encode(id)

def unhash_id(hashed_id: str) -> int:
    unhashed =  hashids.decode(hashed_id)[0]
    if (type(unhashed) == int):
        return unhashed
    else:
        raise Exception("Invalid id")