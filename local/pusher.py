import zounds
from autoencoder import most_recent_id, NoTrainedModelException
import argparse
from config import Sound
from learner import with_hash, Network

queries = [
    'drums',
    'guitar',
    'voice',
    'bass',
    'cello',
    'violin',
    'viola',
    'piano',
    'trombone',
    'trumpet',
    'saxophone',
    'rhodes',
    'moog',
    'synth',
    'birds',
    'ambient',
    'snare',
    'kick',
    'classical',
    'cymbal',
    'tom',
    'triangle',
    'electric',
    'riff',
    'heavy',
    'trance',
    'moan',
    'spooky',
    'scary',
    'evil',
    'xylophone',
    'marimba',
    'bells',
    'bell',
    'hihat',
    'strings',
    'acoustic',
    'crash',
    'ride',
    'metal',
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


# def master_iterator(freesound_api_key):
#     for meta in zounds.PhatDrumLoops():
#         yield meta
#
#     for query in queries:
#         for meta in zounds.FreeSoundSearch(
#                 freesound_api_key, query, n_results=20, delay=1.0):
#             yield meta
#
#     for archive_id in internet_archive_ids:
#         for meta in zounds.InternetArchive(archive_id):
#             yield meta
#
#     mn = zounds.MusicNet(path='/home/user/Downloads')
#     for meta in mn:
#         yield meta
#
#     ns = zounds.NSynth(path='/home/user/Downloads')
#     for meta in ns:
#         yield meta


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--freesound-key',
        type=str,
        required=True,
        help='The FreeSound API key')
    args = parser.parse_args()

    new_id = most_recent_id()

    # try:
    #     cls = with_hash(new_id)
    # except NoTrainedModelException:
    #     cls = Sound

    cls = Sound

    # zounds.ingest(zounds.PhatDrumLoops(), cls, multi_threaded=True)
    #
    # for query in queries:
    #     fss = zounds.FreeSoundSearch(
    #         args.freesound_key, query, n_results=20, delay=1.0)
    #     zounds.ingest(fss, cls, multi_threaded=True)

    # for archive_id in internet_archive_ids:
    #     zounds.ingest(
    #         zounds.InternetArchive(archive_id=archive_id),
    #         cls,
    #         multi_threaded=True)
    #

    # mn = zounds.MusicNet(path='/home/user/Downloads')
    # zounds.ingest(mn, cls, multi_threaded=True)


    ns = zounds.NSynth(path='/home/user/Downloads')
    zounds.ingest(ns, cls, multi_threaded=True)
