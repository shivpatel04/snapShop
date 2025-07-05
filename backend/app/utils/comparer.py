def merge_results(*lists):
    merged = []
    for l in lists:
        merged.extend(l)
    return merged
