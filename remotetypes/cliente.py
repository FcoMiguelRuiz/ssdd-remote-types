import sys
import Ice
import RemoteTypes as rt

def main():
    with Ice.initialize(sys.argv) as communicator:
        proxy = communicator.stringToProxy("factory:default -p 10000")
        factory = rt.FactoryPrx.checkedCast(proxy)
        if not factory:
            raise RuntimeError("Invalid proxy for Factory.")

        print("\n=== Testing RemoteDict ===")
        dict_proxy = factory.get(rt.TypeName.RDict, "test_dict")
        print(f"RemoteDict proxy: {dict_proxy}")
        remote_dict = rt.RDictPrx.checkedCast(dict_proxy)
        if not remote_dict:
            raise RuntimeError("Invalid proxy or type mismatch for RemoteDict.")
        print("Adding entries to RemoteDict...")
        remote_dict.setItem("key1", "value1")
        remote_dict.setItem("key2", "value2")
        remote_dict.setItem("key3", "value3")
        print("Entries added.")
        print("Iterating through the dictionary using a remote iterator:")
        dict_iterator = remote_dict.iter()
        dict_length = remote_dict.length()
        print(f"Dictionary length: {dict_length}")
        dict_count = 0
        while dict_count < dict_length:
            print(dict_iterator.next())
            dict_count += 1

        print("\n=== Testing RemoteList ===")
        list_proxy = factory.get(rt.TypeName.RList, "test_list")
        print(f"RemoteList proxy: {list_proxy}")
        remote_list = rt.RListPrx.checkedCast(list_proxy)
        if not remote_list:
            raise RuntimeError("Invalid proxy or type mismatch for RemoteList.")
        print("Adding entries to RemoteList...")
        remote_list.append("value1")
        remote_list.append("value2")
        remote_list.append("value3")
        print("Entries added.")
        print("Iterating through the list using a remote iterator:")
        list_iterator = remote_list.iter()
        list_length = remote_list.length()
        print(f"List length: {list_length}")
        list_count = 0
        while list_count < list_length:
            print(list_iterator.next())
            list_count += 1

        print("\n=== Testing RemoteSet ===")
        set_proxy = factory.get(rt.TypeName.RSet, "test_set")
        print(f"RemoteSet proxy: {set_proxy}")
        remote_set = rt.RSetPrx.checkedCast(set_proxy)
        if not remote_set:
            raise RuntimeError("Invalid proxy or type mismatch for RemoteSet.")
        print("Adding entries to RemoteSet...")
        remote_set.add("value1")
        remote_set.add("value2")
        remote_set.add("value3")
        print("Entries added.")
        print("Iterating through the set using a remote iterator:")
        set_iterator = remote_set.iter()
        set_length = remote_set.length()
        print(f"Set length: {set_length}")
        set_count = 0
        while set_count < set_length:
            print(set_iterator.next())
            set_count += 1

if __name__ == "__main__":
    main()
