from pymongo import MongoClient


def retrieve_batch(cursor, batch_size=100):
    obj = []
    for elem in cursor:
        obj.append(elem)
    if len(obj) == 0:
        print("No more values to retrieve")
        return False
    if len(obj) < 100:
        print("End of the epoch")
    return obj


class DataGenerator:
    def __init__(
        self,
        batch_size=100,
        epochs=5,
        conn_str="mongodb://49.13.173.177:27020/",
        db="sponsoredbye",
        coll="embeddings",
    ):
        self.conn_str = conn_str
        self.client = MongoClient(conn_str)
        self.db = self.client[db]
        self.coll = self.client[db][coll]
        self.batch_size = batch_size
        self.epochs = epochs
        self.cursor = self.coll.find({})
        self.current_epoch = 0

    def get_data(self):
        """
        Loop over the cursor for batch_size amount. If it runs out, check if we can update epoch
        If we can update epoch, reset the cursor and increment epoch
        """
        data = []
        cntr = 0
        for elem in self.cursor:
            data.append(elem)
            cntr += 1
            if cntr >= self.batch_size:
                break

        if len(data) < self.batch_size:
            # There are no more values, so need to reinitialize the cursor
            if self.current_epoch < self.epochs:
                self.current_epoch += 1
                self.cursor = self.coll.find({})
            else:
                # The generator is done and the epochs have been finished
                return data
            for elem in self.cursor:
                data.append(elem)
                cntr += 1
                if cntr > self.batch_size:
                    break
        return data


if __name__ == "__main__":
    gen = DataGenerator()
    a = gen.get_data()
    b = gen.get_data()
    a_ids = [elem["videoID"] for elem in a]
    b_ids = [elem["videoID"] for elem in b]
    print(len(a), len(b))
    print(f"A ids: {a_ids}")
    print(f"B ids: {b_ids}")
