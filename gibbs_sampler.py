#!/usr/bin/env python
# encoding=utf-8
# Created by: xfulop


"""
    This program is a simple implementation of the Gibbs sampler algorithm for motif finding.
    Using ANSII colors, it prints the best motif found in the sequence.

    Usage:
        gibbs_sampler.py :with deafult parameters
        gibbs_sampler.py <N> <n_iter> :with custom parameters
        -- N: number of iterations inside the Gibbs sampler for sequence selection
        -- n_iter: number of iterations for repeating the Gibbs sampler

    Output:
        -- plot of the best score found in each iteration
        -- txt file with the best motifs found in each iteration highlighted in red
        -- to open txt file in terminal: cat <filename> | less -R    
"""


import sys
import matplotlib.pyplot as plt
import seaborn as sns
import random

dna = [
    "TTACCTTAAC",
    "GATGTCTGTC",
    "CCGGCGTTAG",
    "CACTAACGAG",
    "CGTCAGAGGT"
]



def gibbs_sampler(dna, k, t, N):
    # randomly select k-mers as the initial motifs
    motifs = []
    for seq in dna:
        i = random.randint(0, len(seq) - k)
        motifs.append(seq[i:i+k])
    best_motifs = motifs.copy()
    
    # perform N iterations of the algorithm
    for _ in range(N):
        i = random.randint(0, t-1)
        motif_i = motifs[i]
        motifs.pop(i)
        
        # build the profile matrix from the other motifs
        profile = build_profile_matrix(motifs)
        
        # generate a new k-mer based on the profile matrix
        motif_i = profile_randomly_generated_kmer(dna[i], k, profile)
        
        motifs.insert(i, motif_i)
        
        # update the best motifs if necessary
        if score_motif(motifs) < score_motif(best_motifs):
            best_motifs = motifs.copy()

        # print best motifs highlighted in red using ANSI escape sequences using and original sequences
        gibbs_motifs = []
        for i in range(len(best_motifs)):
            gibbs_motif_all = dna[i].replace(best_motifs[i], "\033[31m"+best_motifs[i]+"\033[0m")
            gibbs_motifs.append(gibbs_motif_all)

        consensus_motif = consensus(best_motifs)

    return best_motifs, score_motif(best_motifs), gibbs_motifs, consensus_motif

def build_profile_matrix(motifs):
    # build the profile matrix from the motifs
    profile = [[0 for _ in range(4)] for _ in range(len(motifs[0]))]
    for i in range(len(motifs[0])):
        column = [motif[i] for motif in motifs]
        for j in range(4):
            profile[i][j] = (column.count(j) + 1) / (len(motifs) + 4)
    return profile

def profile_randomly_generated_kmer(seq, k, profile):
    # generate a new k-mer based on the profile matrix
    n = len(seq)
    probabilities = []
    for i in range(n - k + 1):
        kmer = seq[i:i+k]
        prob = 1
        for j in range(k):
            if kmer[j] == 'A':
                prob *= profile[j][0]
            elif kmer[j] == 'C':
                prob *= profile[j][1]
            elif kmer[j] == 'G':
                prob *= profile[j][2]
            elif kmer[j] == 'T':
                prob *= profile[j][3]
        probabilities.append(prob)
    probabilities = [p/sum(probabilities) for p in probabilities]
    i = random.choices(range(n - k + 1), weights=probabilities)[0]
    return seq[i:i+k]

def score_motif(motif):
    # calculate the score of a single motif
    consensus = ''
    score = 0
    for i in range(len(motif[0])):
        counts = [0, 0, 0, 0]
        for j in range(len(motif)):
            if motif[j][i] == 'A':
                counts[0] += 1
            elif motif[j][i] == 'C':
                counts[1] += 1
            elif motif[j][i] == 'G':
                counts[2] += 1
            elif motif[j][i] == 'T':
                counts[3] += 1
        max_count = max(counts)
        if max_count == counts[0]:
            consensus += 'A'
        elif max_count == counts[1]:
            consensus += 'C'
        elif max_count == counts[2]:
            consensus += 'G'
        elif max_count == counts[3]:
            consensus += 'T'
        for j in range(len(motif)):
            if motif[j][i] != consensus[i]:
                score += 1
    return score


def consensus(motifs):
    # calculate the consensus string of a set of final motifs
    consensus = ''
    for i in range(len(motifs[0])):
        counts = [0, 0, 0, 0]
        for j in range(len(motifs)):
            if motifs[j][i] == 'A':
                counts[0] += 1
            elif motifs[j][i] == 'C':
                counts[1] += 1
            elif motifs[j][i] == 'G':
                counts[2] += 1
            elif motifs[j][i] == 'T':
                counts[3] += 1
        max_count = max(counts)
        if max_count == counts[0]:
            consensus += 'A'
        elif max_count == counts[1]:
            consensus += 'C'
        elif max_count == counts[2]:
            consensus += 'G'
        elif max_count == counts[3]:
            consensus += 'T'

    return consensus


def visualize_until_convergence(score_lst):
    # visualize score after each iteration
    sns.set_style('whitegrid')
    plt.figure(figsize=(15,5))
    plt.plot(score_lst)
    plt.xlabel('Iteration')
    plt.ylabel('Score')
    plt.title('Gibbs Sampler Convergence')

    # find the lowest score and the iteration at which it occurs
    min_score = min(score_lst[int(0.2 * len(score_lst)):])
    min_score_iter = score_lst.index(min_score)

    # plot burn-in period in blue
    plt.fill_between(range(int(0.1 * len(score_lst))), score_lst[:int(0.1 * len(score_lst))], color='blue', alpha=0.1)

    # plot min score with red point
    plt.scatter(min_score_iter, min_score, color='red', s=100)
    
    # y lim from 4 to 12
    plt.ylim(4,12)

    # legend
    plt.legend(['Score after each iteration',
                'Burn-in period',
                'Min score {0} after iteration {1}'.format(min_score, min_score_iter)
                ])
    plt.savefig('gibbs_sampler_plot.png')
    plt.show()




score_lst = []

def RepeatGibbsMotSearch(k, t, N, n_times):
    """
    the RepeatGibbsMotSearch function has been modified to repeat the Gibbs sampling 
    process n_times and then sort and print the best motifs found for each iteration. 
    This function is then wrapped with another loop that repeats the entire process N times.
    This outer loop allows the entire sampling process to be repeated multiple times, while 
    the inner loop repeats the process n_times to find the best motifs within each iteration.
    """
    with open('gibbs_sampling_results.txt', 'w') as f:  # update the mode parameter
        for N_iter in range(N):
            motif_lst = []
            all_gibs_motifs_lst = []
            consensus_lst = []
            for _ in range(n_times):
                motif, score, gibbs_motifs, consensus = gibbs_sampler(dna, k, t, N)
                motif_lst.append(motif)
                score_lst.append(score)
                all_gibs_motifs_lst.append(gibbs_motifs)
                consensus_lst.append(consensus)

            # sort the motifs by score
            data = list(zip(score_lst, all_gibs_motifs_lst, consensus_lst))
            data.sort(key=lambda x: x[0])

            f.write(f'N = {N_iter+1} of {N}\n')
            f.write(f'Consensus: {consensus_lst[0]}\n')
            f.write(f'Score = {score_lst[0]} \n')
            f.write('Motifs found after iterations:')
            for j in range(len(all_gibs_motifs_lst[0])):
                f.write(f'{all_gibs_motifs_lst[0][j]}\n')
            f.write('**********************************************\n')


def main():
    k = 4
    t = 5
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 30  # inside gibbs fnc
    n_times = int(sys.argv[2]) if len(sys.argv) > 2 else 60  # outside gibbs fnc, just repeat all 

    print(f'Running Gibbs Sampler {n_times} times, {N} iterations each')
    RepeatGibbsMotSearch(k, t, N, n_times)
    print("Visualizing results...")
    visualize_until_convergence(score_lst)
    print('Done')


if __name__ == '__main__':
    main()