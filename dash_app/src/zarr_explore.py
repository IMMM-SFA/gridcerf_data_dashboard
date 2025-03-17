import zarr

# Open your Zarr store (assuming it’s a directory)
path = "/Users/bern700/git_repositories/IMMM-SFA/data/zarr_output.zarr"
store = zarr.DirectoryStore(path)
print('here')
root = zarr.open(store, mode='r')
print(root.tree())
# zarr.consolidate_metadata(store)
