import zounds
from config import soundalike_client
import argparse

queries = [
    # 'drums',
    # 'guitar',
    # 'voice',
    # 'bass',
    # 'cello',
    # 'violin',
    # 'viola',
    # 'piano',
    # 'trombone',
    # 'trumpet',
    # 'saxophone',
    # 'rhodes',
    # 'moog',
    # 'synth',
    # 'birds',
    # 'ambient',
    # 'snare',
    # 'kick',
    # 'classical',
    # 'cymbal',
    # 'tom',
    # 'triangle',
    # 'electric',
    # 'riff',
    # 'heavy',
    # 'trance',
    # 'moan',
    # 'spooky',
    # 'scary',
    # 'evil',
    # 'xylophone',
    # 'marimba',
    # 'bells',
    # 'bell',
    # 'hihat',
    # 'strings',
    # 'acoustic',
    # 'crash',
    # 'ride',
    # 'metal',
    'rock'
]

internet_archive_ids = [
    'AOC11B',
    'Kevin_Gates_-_By_Any_Means-2014',
    'Chance_The_Rapper_-_Coloring_Book',
    'CHOPINEtudes-Cortot-NEWTRANSFER',
    'Greatest_Speeches_of_the_20th_Century',
    'siguesigue-1988'
]


def master_iterator(freesound_api_key):
    for meta in list(zounds.PhatDrumLoops())[:3]:
        yield meta

    for query in queries:
        for meta in zounds.FreeSoundSearch(
                freesound_api_key, query, n_results=3, delay=1.0):
            yield meta

    for archive_id in internet_archive_ids:
        for meta in list(zounds.InternetArchive(archive_id))[:1]:
            yield meta


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--freesound-key',
        type=str,
        required=True,
        help='The FreeSound API key')
    args = parser.parse_args()

    for meta in master_iterator(args.freesound_key):
        data = dict(**meta.__dict__)
        data['uri'] = meta.uri.url
        print data
        soundalike_client.add_sound(data)
